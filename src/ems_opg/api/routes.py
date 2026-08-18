import csv
import io
from datetime import UTC, datetime
import logging, shutil
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from ems_opg.core.constants import APP_VERSION
from ems_opg.core.validators import is_valid_serial_number
from ems_opg.database.database import DatabaseManager
from ems_opg.database.engine import DATABASE_FILE
from ems_opg.database.models import AuditLog, Device
from ems_opg.repositories.audit_repository import AuditRepository
from ems_opg.repositories.device_repository import DeviceRepository
from ems_opg.repositories.mac_address_repository import MacAddressRepository
from ems_opg.repositories.order_repository import OrderRepository
from ems_opg.services.device_service import DeviceService
from ems_opg.services.order_service import OrderService
from ems_opg.services.qr_service import QRService
from ems_opg.workflow.workflow_engine import WorkflowEngine
from ems_opg.workflow.workflow_state import WorkflowState

LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}

CSV_HEADER = ["Date", "Order", "Serial", "MAC1", "MAC2", "Operator", "Result", "Status"]


def device_csv_row(d):
    return [
        d.timestamp.isoformat() if d.timestamp else "",
        d.order_number,
        d.serial_number,
        d.ethaddr_id,
        d.eth1addr_id or "",
        d.operator,
        d.test_result,
        "Used" if d.used else "Available",
    ]

def write_devices_csv(writer, devices):
    writer.writerow(CSV_HEADER)
    for d in devices:
        writer.writerow(device_csv_row(d))

def session_dict(session):
    return {
        "operator": session.operator,
        "order_number": session.order_number,
        "serial_number": session.serial_number,
        "mac1": session.mac1,
        "mac2": session.mac2,
        "test_result": session.test_result,
        "test_notes": session.test_notes,
        "current_step": session.current_step,
        "total_steps": session.total_steps,
        "completed": session.completed,
        "cancelled": session.cancelled,
    }


def device_dict(device):
    return {
        "id": device.id,
        "order_number": device.order_number,
        "serial_number": device.serial_number,
        "ethaddr_id": device.ethaddr_id,
        "eth1addr_id": device.eth1addr_id,
        "used": device.used,
        "test_result": device.test_result,
        "operator": device.operator,
        "timestamp": device.timestamp.isoformat() if device.timestamp else None,
    }
    
def maybe_export_completed_order(db_session, application, order_number):
    """
    If every device tied to order_number has been finalized with a PASS
    result, write the order's traceability records to exports/ as a CSV.
    No-ops (silently) if the order isn't fully passed yet.
    """

    order_repo = OrderRepository(db_session)
    device_repo = DeviceRepository(db_session)

    order = order_repo.get_by_order_number(order_number)
    if order is None:
        return

    devices = device_repo.list_by_order(order_number)

    if not devices or not all(d.used for d in devices):
        return

    if not all(d.test_result == "PASS" for d in devices):
        return

    try:
        application.paths.exports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        destination = application.paths.exports_dir / f"{order_number}_{timestamp}.csv"

        with destination.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            write_devices_csv(writer, devices)

    except OSError:
        application.logger.exception(
            "Failed to export completed order %s to CSV.", order_number
        )


def build_step_payload(engine, qr_service):
    session = engine.session
    index = session.current_step
    step_name = engine.current_step_name()

    if index == 0:
        result = qr_service.create_step1()
    elif index == 1:
        result = qr_service.create_step2()
    elif index == 2:
        command = qr_service.multi_step()
        result = qr_service.generator.generate(command, "step3")
    elif index == 3:
        result = qr_service.create_step8()
    elif index == 4:
        if not (session.mac1 and session.mac2):
            return {
                "workflow_name": "Functional Test",
                "step_index": index,
                "step_number": index + 1,
                "total_steps": session.total_steps,
                "step_name": step_name,
                "command": "",
                "qr_url": None,
            }
        command = qr_service.create_macs(session.mac1, session.mac2)
        result = qr_service.generator.generate(command, "step5")
    else:
        command = qr_service.create_step11()
        result = qr_service.generator.generate(command, "step6")

    return {
        "workflow_name": "Functional Test",
        "step_index": index,
        "step_number": index + 1,
        "total_steps": session.total_steps,
        "step_name": step_name,
        "command": result.command,
        "qr_url": f"/qr/{result.filename}",
    }


def register_routes(app, application):
    api_bp = Blueprint("api", __name__, url_prefix="/api")

    engine = WorkflowEngine()
    qr_service = QRService(output_directory=application.paths.qr_cache)

    def session_active():
        return engine.state in (WorkflowState.TESTING, WorkflowState.COMPLETE)

    def workflow_response():
        return jsonify({
            "session": session_dict(engine.session),
            "step": build_step_payload(engine, qr_service),
        })

    @api_bp.route("/status", methods=["GET"])
    def status():
        db = DatabaseManager()
        db_connected = db.health_check()

        devices_today = 0
        if db_connected:
            today = datetime.now(UTC).date()
            with db.session() as db_session:
                devices_today = sum(
                    1
                    for device in db_session.query(Device).all()
                    if device.timestamp and device.timestamp.date() == today
                )

        return jsonify({
            "version": APP_VERSION,
            "databaseConnected": db_connected,
            "workflowReady": True,
            "devicesToday": devices_today,
        })

    @api_bp.route("/orders/provision", methods=["POST"])
    def provision_order():
        payload = request.get_json(silent=True) or {}
        order_number = (payload.get("order_number") or "").strip()
        part_number = (payload.get("part_number") or "").strip()

        if not order_number or not part_number:
            return jsonify({"error": "order_number and part_number are required"}), 400

        try:
            quantity = int(payload.get("quantity"))
        except (TypeError, ValueError):
            return jsonify({"error": "quantity must be a whole number."}), 400

        db = DatabaseManager()

        try:
            with db.session() as db_session:
                order_service = OrderService(db_session)
                result = order_service.provision_order(order_number, part_number, quantity)
        except ValueError as error:
            return jsonify({"error": str(error)}), 409
        except IntegrityError:
            return jsonify({
                "error": (
                    "Could not provision this order because the MAC address pool "
                    "and device records are out of sync (a MAC marked available "
                    "is already assigned to an existing device). This needs an "
                    "administrator to reconcile the database before provisioning can continue"
                ),
            }), 409
            

        return jsonify({"message": result["message"]}), 201

    @api_bp.route("/orders/open", methods=["GET"])
    def get_open_orders():
        db = DatabaseManager()

        with db.session() as db_session:
            order_repo = OrderRepository(db_session)
            device_repo = DeviceRepository(db_session)

            open_orders = []
            for order in order_repo.list_all_orders():
                devices = device_repo.list_by_order(order.order_number)
                completed = sum(1 for device in devices if device.used)

                if completed < order.quantity:
                    open_orders.append({
                        "order_number": order.order_number,
                        "part_number": order.part_number,
                        "quantity": order.quantity,
                        "completed": completed,
                        "device_count": len(devices),
                    })

            return jsonify({"orders": open_orders})

    @api_bp.route("/orders/<order_number>", methods=["DELETE"])
    def delete_order(order_number):
        payload = request.get_json(silent=True) or {}
        operator = (payload.get("operator") or "").strip() or "system"

        db = DatabaseManager()

        with db.session() as db_session:
            order_repo = OrderRepository(db_session)
            device_repo = DeviceRepository(db_session)
            audit_repo = AuditRepository(db_session)

            order = order_repo.get_by_order_number(order_number)
            if order is None:
                return jsonify({"error": "Order not found"}), 404

            devices = device_repo.list_by_order(order_number)

            if not devices:
                order_repo.delete(order)
                audit_repo.create(AuditLog(
                    operator=operator,
                    action="Order Deleted",
                    details=f"Empty order {order_number} deleted (no devices attached).",
                ))
                return jsonify({"message": f"Order {order_number} deleted."})

            # Orders with devices attached can't have their row removed
            # (devices.order_number is a required foreign key), and their
            # MAC addresses stay claimed either way. Instead, reset every
            # device back to available so a mis-provisioned order (too many
            # or too few devices assigned) can be corrected and re-tested -
            # serial numbers, operators, and MAC assignments are untouched.
            for device in devices:
                device.used = False

            audit_repo.create(AuditLog(
                operator=operator,
                action="Order Reset",
                details=(
                    f"Order {order_number} reset: {len(devices)} device(s) "
                    "marked available again (MAC addresses, serial numbers, "
                    "and operators left unchanged)."
                ),
            ))

            return jsonify({
                "message": (
                    f"Order {order_number} reset: {len(devices)} device(s) "
                    "marked available."
                ),
            })


    @api_bp.route("/session/start", methods=["POST"])
    def session_start():
        payload = request.get_json(silent=True) or {}
        operator = (payload.get("operator") or "").strip()
        order_number = (payload.get("order_number") or "").strip()

        if not operator or not order_number:
            return jsonify({"error": "operator and order_number are required"}), 400

        db = DatabaseManager()
        with db.session() as db_session:
            device_repo = DeviceRepository(db_session)
            next_device = device_repo.get_next_unused_by_order(order_number)

        if next_device is None:
            return jsonify({
                "error": f"No unprovisioned devices remain for order {order_number}.",
            }), 409

        engine.start(operator, order_number)
        engine.set_mac_addresses(next_device.ethaddr_id, next_device.eth1addr_id)

        return workflow_response()

    @api_bp.route("/workflow", methods=["GET"])
    def workflow_get():
        if not session_active():
            return jsonify({"error": "No active session"}), 404

        return workflow_response()

    @api_bp.route("/workflow/next", methods=["POST"])
    def workflow_next():
        if not session_active():
            return jsonify({"error": "No active session"}), 404

        engine.next_step()

        return workflow_response()

    @api_bp.route("/workflow/previous", methods=["POST"])
    def workflow_previous():
        if not session_active():
            return jsonify({"error": "No active session"}), 404

        engine.previous_step()

        return workflow_response()

    @api_bp.route("/workflow/mac", methods=["PUT"])
    def workflow_mac():
        if not session_active():
            return jsonify({"error": "No active session"}), 404

        payload = request.get_json(silent=True) or {}
        mac1 = (payload.get("mac1") or "").strip()
        mac2 = (payload.get("mac2") or "").strip()

        if not mac1 or not mac2:
            return jsonify({"error": "mac1 and mac2 are required"}), 400

        engine.set_mac_addresses(mac1, mac2)

        return workflow_response()
    
    @api_bp.route("/workflow/result", methods=["PUT"])
    def workflow_result():
        if not session_active():
            return jsonify({"error": "No active session"}), 400
        
        if engine.state != WorkflowState.COMPLETE:
            return jsonify({"error": "Complete all test steps before recording a result"}), 409
        
        payload = request.get_json(silent=True) or {}
        result = (payload.get("result") or"").strip().upper()
        notes = (payload.get("notes") or "").strip()
        
        if result not in ("PASS", "FAIL"):
            return jsonify({"error": "result must be PASS or FAIL"}), 400
        
        if result == "FAIL" and not notes:
            return jsonify({"error": "Notes are required when recording a failed test."}), 400
        
        engine.set_test_result(result, notes)
        
        return workflow_response()

    @api_bp.route("/session/finish", methods=["POST"])
    def session_finish():
        if not session_active():
            return jsonify({"error": "No active session"}), 404
        
        if engine.session.test_result not in ("PASS", "FAIL"):
            return jsonify({"error": "Record a test result before saving this device"}), 409

        payload = request.get_json(silent=True) or {}
        serial_number = (payload.get("serial_number") or "").strip()

        if not serial_number:
            return jsonify({"error": "serial_number is required"}), 400

        if not is_valid_serial_number(serial_number):
            return jsonify({"error": "Serial number must be formatted as EMyyyyww0000."}), 400

        db = DatabaseManager()

        try:
            with db.session() as db_session:
                device_service = DeviceService(db_session)
                device_service.reserve_device(
                    ethaddr_id=engine.session.mac1,
                    eth1addr_id=engine.session.mac2,
                    order_number=engine.session.order_number,
                    serial_number=serial_number,
                    operator=engine.session.operator,
                    test_result=engine.session.test_result,
                )
                
                if engine.session.test_result == "FAIL":
                    audit_repo = AuditRepository(db_session)
                    audit_repo.create(AuditLog(
                        operator=engine.session.operator or "unknown",
                        action="Test Failed",
                        details=(
                            f"Device {serial_number} (order {engine.session.order_number}) "
                            f"failed testings. Notes: {engine.session.test_notes}"
                        ),
                    ))
                    
                maybe_export_completed_order(db_session, application, engine.session.order_number)
        except ValueError as error:
            return jsonify({"error": str(error)}), 409

        engine.finish(serial_number)

        return jsonify({
            "session": session_dict(engine.session),
            "message": "Device saved to traceability log.",
            "serial_number": serial_number,
        })

    @api_bp.route("/session/cancel", methods=["POST"])
    def session_cancel():
        engine.cancel()
        return jsonify({"success": True})

    @api_bp.route("/logging/level", methods=["PUT"])
    def set_logging_level():
        payload = request.get_json(silent=True) or {}
        level = (payload.get("level") or "").strip().upper()

        if level not in LOG_LEVELS:
            return jsonify({"error": f"Unknown log level: {level}"}), 400
        
        numeric_level = getattr(logging, level)
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # Some libraries (sqlalchemy's echo=True, werkzeug's dev server) set
        # their own logger level, which would otherwise override an inherited
        # root level. Setting the level on the root's handlers instead filters
        # everything that reaches them, regardless of the originating logger.
        for handler in root_logger.handlers:
            handler.setLevel(numeric_level)
        

        return jsonify({"message": f"Log level set to {level}."})

    @api_bp.route("/config/reload", methods=["POST"])
    def reload_config():
        try:
            application.config.load()
        except Exception as error:
            return jsonify({"error": f"Unable to reload configuration"}), 500

        return jsonify({"message": "Configuration reloaded"})

    @api_bp.route("/cache/regenerate", methods=["POST"])
    def regenerate_cache():
        removed = 0
        for qr_file in application.paths.qr_cache.glob("*.png"):
            qr_file.unlink()
            removed += 1

        return jsonify({
            "message": f"QR cache cleared ({removed} file(s)). "
            "Images will regenerate the next time each step is displayed."
        })

    @api_bp.route("/database/verify", methods=["POST"])
    def verify_database():
        db = DatabaseManager()

        if db.health_check():
            return jsonify({"message": "Database verification passed"})

        return jsonify({"error": "Databse verification failed - unable to connect."}), 404

    @api_bp.route("/database/backup", methods=["POST"])
    def backup_database():
        source = DATABASE_FILE

        if not DATABASE_FILE.exists():
            return jsonify({"error": "No database file found to back up"}), 404

        db = DatabaseManager()
        max_backups = application.config.backup.get("max_backups", 5)
        destination = db.backup(DATABASE_FILE, application.paths.backup_dir, keep=max_backups)

        return jsonify({"message": f"Database backed up to {destination.name}."})

    @api_bp.route("/database/restore", methods=["POST"])
    def restore_database():
        backups = sorted(
            application.paths.backup_dir.glob("ems_opg_*.db"),
            key=lambda path: path.stat().st_mtime,
        )

        if not backups:
            return jsonify({"error": "No backups found to restore."}), 404

        latest = backups[-1]
        shutil.copy2(latest, DATABASE_FILE)

        return jsonify({
            "message": f"Database restored from {latest.name}. "
            "Restart the server to ensure the change takes effect."
        })

    @api_bp.route("/devices/<serial>", methods=["GET"])
    def get_device(serial):
        db = DatabaseManager()

        with db.session() as db_session:
            repo = DeviceRepository(db_session)
            device = repo.get_by_serial(serial)

            if device is None:
                return jsonify({"error": "Device not found"}), 404

            return jsonify({"device": device_dict(device)})

    @api_bp.route("/devices/<serial>", methods=["PUT"])
    def update_device(serial):
        payload = request.get_json(silent=True) or {}

        order_number = (payload.get("order_number") or "").strip()
        new_serial = (payload.get("serial_number") or "").strip()
        operator = (payload.get("operator") or "").strip()
        mac1 = (payload.get("mac1") or "").strip()
        mac2 = (payload.get("mac2") or "").strip()
        reason = (payload.get("reason") or "").strip()

        if not order_number or not new_serial or not mac1:
            return jsonify({"error": "order_number, serial_number, and mac1 are required"}), 400

        if not reason:
            return jsonify({"error": "A reason is required for manual corrections."}), 400

        if not is_valid_serial_number(new_serial):
            return jsonify({"error": "Serial number must be formatted as EMyyyyww0000."}), 400

        db = DatabaseManager()

        with db.session() as db_session:
            repo = DeviceRepository(db_session)
            device = repo.get_by_serial(serial)

            if device is None:
                return jsonify({"error": "Device not found"}), 404

            if new_serial != device.serial_number and repo.get_by_serial(new_serial) is not None:
                return jsonify({"error": "Serial number already exists."}), 409

            before = device_dict(device)
            
            old_mac1, old_mac2 = device.ethaddr_id, device.eth1addr_id
            new_mac2 = mac2 or None

            if old_mac1 != mac1 or old_mac2 != new_mac2:
                mac_repo = MacAddressRepository(db_session)
                new_macs = {mac1, new_mac2}
                
                for candidate in (mac1, new_mac2):
                    if not candidate:
                        continue
                    conflict = repo.get_by_single_mac(candidate)
                    if conflict is not None and conflict.id != device.id:
                        return jsonify({"error": f"MAC address {candidate} is already assigned to another device."}), 409

                for old_mac in (old_mac1, old_mac2):
                    if old_mac and old_mac not in new_macs:
                        old_entry = mac_repo.get_by_mac(old_mac)
                        if old_entry is not None:
                            mac_repo.mark_unused(old_entry)

                for claimed_mac in (mac1, new_mac2):
                    if claimed_mac:
                        claimed_entry = mac_repo.get_by_mac(claimed_mac)
                        if claimed_entry is not None:
                            mac_repo.mark_used(claimed_entry)

            device.order_number = order_number
            device.serial_number = new_serial
            device.operator = operator
            device.ethaddr_id = mac1
            device.eth1addr_id = new_mac2
            audit_repo = AuditRepository(db_session)
            audit_repo.create(AuditLog(
                operator=operator or "unknown",
                action="Manual Correction",
                details=f"Device {before['serial_number']} corrected by {operator or 'unknown'}. Reason: {reason}",
            ))

            return jsonify({
                "device": device_dict(device),
                "message": "Device updated successfully.",
            })

    @api_bp.route("/devices/<serial>/reset-mac", methods=["POST"])
    def reset_device_mac(serial):
        payload = request.get_json(silent=True) or {}
        reason = (payload.get("reason") or "").strip()

        if not reason:
            return jsonify({"error": "A reason is required to reset a MAC address."}), 400

        db = DatabaseManager()

        with db.session() as db_session:
            repo = DeviceRepository(db_session)
            device = repo.get_by_serial(serial)

            if device is None:
                return jsonify({"error": "Device not found"}), 404

            repo.mark_unused(device)
            
            # Only clears the device's "used" flag so the same MAC pair can
            # be re-finished (corrected serial/order). The MAC pool entries
            # stay marked used — a MAC is permanently tied to one physical
            # device's unique columns, so freeing the pool here would let
            # provisioning try to hand these same MACs to a *different*
            # device and crash on the devices table's UNIQUE constraint.        

            audit_repo = AuditRepository(db_session)
            audit_repo.create(AuditLog(
                operator=device.operator or "unknown",
                action="MAC Reset",
                details=f"MAC used-status reset for device {device.serial_number}. Reason: {reason}",
            ))

            return jsonify({
                "device": device_dict(device),
                "message": "MAC reset successfully.",
            })

    @api_bp.route("/mac/<mac>", methods=["GET"])
    def get_device_by_mac(mac):
        db = DatabaseManager()

        with db.session() as db_session:
            repo = DeviceRepository(db_session)
            device = repo.get_by_single_mac(mac)

            if device is None:
                return jsonify({"error": "Device not found"}), 404

            return jsonify({"device": device_dict(device)})

    @api_bp.route("/history", methods=["GET"])
    def get_history():
        query = (request.args.get("q") or "").strip()
        db = DatabaseManager()

        with db.session() as db_session:
            repo = DeviceRepository(db_session)
            devices = repo.search(query) if query else repo.list_all()

            return jsonify({"records": [device_dict(d) for d in devices]})

    @api_bp.route("/history/export", methods=["GET"])
    def export_history():
        db = DatabaseManager()

        with db.session() as db_session:
            repo = DeviceRepository(db_session)
            devices = repo.list_all()

            buffer = io.StringIO()
            writer = csv.writer(buffer)
            write_devices_csv(writer, devices)
           
            return jsonify({"csv": buffer.getvalue(), "filename": "ems-opg-history.csv"})

    @api_bp.route("/mac-pool", methods=["GET"])
    def get_mac_pool():
        db = DatabaseManager()

        with db.session() as db_session:
            mac_repo = MacAddressRepository(db_session)
            device_repo = DeviceRepository(db_session)

            records = []
            for entry in mac_repo.list_all():
                device = device_repo.get_by_single_mac(entry.mac_address)
                records.append({
                    "mac_address": entry.mac_address,
                    "used": entry.used,
                    "order_number": device.order_number if device else None,
                    "serial_number": device.serial_number if device else None,
                })

            return jsonify({"records": records})

    @api_bp.route("/reset-device", methods=["GET"])
    def get_reset_device():
        steps = qr_service.create_reset_sequence()

        instructions = (
            "RESET INSTRUCTIONS\n\n"
            "1. Press and hold the erase button\n\n"
            "2. With button pressed, apply power\n\n"
            "3. Once text is seen press any arrow key to cancel the boot "
            "(only a few seconds to do so)\n\n"
            "4. scan the following barcodes"
        )

        return jsonify({"instructions": instructions, "steps": steps})

    app.register_blueprint(api_bp)
