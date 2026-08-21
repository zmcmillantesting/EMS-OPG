import csv
import io
import time
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
from ems_opg.repositories.order_failure_repository import OrderFailureRepository

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

def session_dict(session, state):
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
        # Explicit state name - current_step/test_result/mac1 can't
        # disambiguate every phase on their own (ASSIGNING_MAC once both
        # MACs are set is field-for-field identical to VERIFYING_MAC, and
        # to a save-ready PASS). The frontend switches on this directly.
        "state": state.name,
    }

def failure_note_dict(note):
    return {
        "timestamp": note.timestamp.isoformat() if
        note.timestamp else None,
        "operator": note.operator,
        "reason": note.reason
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

def resolve_device_by_serial(repo, serial, current_order_number):
    """
    Serial numbers are only unique within an order, so a bare serial can
    match devices in more than one order. If current_order_number is
    given, look up that exact (order, serial) pair. Otherwise, require
    the serial to be unambiguous on its own - returns (device, error)
    where error is an (error_response, status) tuple to return as-is,
    or None if a single device was resolved successfully.
    """
    if current_order_number:
        device = repo.get_by_order_and_serial(current_order_number, serial)
        if device is None:
            return None, ({"error": "Device not found"}, 404)
        return device, None

    matches = repo.list_by_serial(serial)

    if not matches:
        return None, ({"error": "Device not found"}, 404)

    if len(matches) > 1:
        return None, ({
            "error": (
                f"Serial {serial} matches devices in more than one order - "
                "include current_order_number to specify which one."
            ),
            "candidates": [device_dict(d) for d in matches],
        }, 409)

    return matches[0], None
    
FAILURE_CSV_HEADER = ["Timestamp", "Operator", "Reason"]


def write_failures_csv(writer, failures):
    writer.writerow(FAILURE_CSV_HEADER)
    for f in failures:
        writer.writerow([
            f.timestamp.isoformat() if f.timestamp else "",
            f.operator,
            f.reason,
        ])


def maybe_export_completed_order(db_session, application, order_number):
    order_repo = OrderRepository(db_session)
    device_repo = DeviceRepository(db_session)

    order = order_repo.get_by_order_number(order_number)
    if order is None:
        return

    passed = device_repo.count_passed_by_order(order_number)
    if passed < order.quantity:
        return

    devices = device_repo.list_by_order(order_number)
    failures = OrderFailureRepository(db_session).list_by_order(order_number)

    try:
        application.paths.exports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

        devices_path = application.paths.exports_dir / f"{order_number}_{timestamp}.csv"
        with devices_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            write_devices_csv(writer, devices)

        if failures:
            failures_path = application.paths.exports_dir / f"{order_number}_{timestamp}_failures.csv"
            with failures_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                write_failures_csv(writer, failures)

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
    else:
        result = qr_service.create_step8()

    return {
        "workflow_name": "Functional Test",
        "step_index": index,
        "step_number": index + 1,
        "total_steps": session.total_steps,
        "step_name": step_name,
        "command": result.command,
        "qr_url": f"/qr/{result.filename}?t={time.time_ns()}",
    }


def build_mac_payload(session, qr_service):
    """WorkflowState.ASSIGNING_MAC - no QR until both MACs are known."""
    if not (session.mac1 and session.mac2):
        return {
            "workflow_name": "Functional Test",
            "step_name": "Mac Addresses",
            "command": "",
            "qr_url": None,
        }

    command = qr_service.create_macs(session.mac1, session.mac2)
    result = qr_service.generator.generate(command, "step5")

    return {
        "workflow_name": "Functional Test",
        "step_name": "Mac Addresses",
        "command": result.command,
        "qr_url": f"/qr/{result.filename}?t={time.time_ns()}",
    }


def build_verification_payload(qr_service):
    """WorkflowState.VERIFYING_MAC"""
    command = qr_service.create_step11()
    result = qr_service.generator.generate(command, "step6")

    return {
        "workflow_name": "Functional Test",
        "step_name": "Verify MAC Addresses",
        "command": result.command,
        "qr_url": f"/qr/{result.filename}?t={time.time_ns()}",
    }

def build_serial_payload(session):
    """WorkflowState.AWAITING_SERIAL - no QR here, just a prompt."""
    return {
        "workflow_name": "Functional Test",
        "step_name": "Serial Number",
        "command": "",
        "qr_url": None,
    }


def register_routes(app, application):
    api_bp = Blueprint("api", __name__, url_prefix="/api")

    engine = WorkflowEngine()
    qr_service = QRService(output_directory=application.paths.qr_cache)

    def session_active():
        return engine.state in (
            WorkflowState.TESTING,
            WorkflowState.AWAITING_RESULT,
            WorkflowState.AWAITING_SERIAL,
            WorkflowState.ASSIGNING_MAC,
            WorkflowState.VERIFYING_MAC,
            WorkflowState.READY_TO_SAVE,
        )

    def workflow_response():
        session = engine.session

        if engine.state == WorkflowState.TESTING:
            step = build_step_payload(engine, qr_service)
        elif engine.state == WorkflowState.AWAITING_SERIAL:
            step = build_serial_payload(session)
        elif engine.state == WorkflowState.ASSIGNING_MAC:
            step = build_mac_payload(session, qr_service)
        elif engine.state == WorkflowState.VERIFYING_MAC:
            step = build_verification_payload(qr_service)
        else:
            step = None

        return jsonify({
            "session": session_dict(session, engine.state),
            "step": step,
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

    @api_bp.route("/orders", methods=["GET", "POST"])
    def orders_collection():
        db = DatabaseManager()

        if request.method == "POST":
            payload = request.get_json(silent=True) or {}
            order_number = (payload.get("order_number") or "").strip()

            try:
                quantity = int(payload.get("quantity"))
            except (TypeError, ValueError):
                return jsonify({"error": "quantity must be a whole number."}), 400

            if not order_number:
                return jsonify({"error": "order_number is required"}), 400

            try:
                with db.session() as db_session:
                    order_service = OrderService(db_session)
                    order = order_service.create_order(order_number, quantity)
                    order_number, quantity = order.order_number, order.quantity
            except ValueError as error:
                return jsonify({"error": str(error)}), 409

            return jsonify({
                "message": f"Order {order_number} created.",
                "order_number": order_number,
                "quantity": quantity,
            }), 201

        # GET - the operator's order dropdown, with live progress against
        # each order's target quantity.
        with db.session() as db_session:
            order_repo = OrderRepository(db_session)
            device_repo = DeviceRepository(db_session)

            orders = []
            for order in order_repo.list_all_orders():
                passed = device_repo.count_passed_by_order(order.order_number)
                orders.append({
                    "order_number": order.order_number,
                    "quantity": order.quantity,
                    "passed": passed,
                    "remaining": max(order.quantity - passed, 0),
                })

            return jsonify({"orders": orders})
        
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
            if devices:
                return jsonify({
                    "error": (
                        f"Order {order_number} has {len(devices)} device(s) "
                        "recorded against it and can't be deleted. Use the "
                        "quantity correction instead if it was mis-entered."
                    ),
                }), 409

            order_repo.delete(order)
            audit_repo.create(AuditLog(
                operator=operator,
                action="Order Deleted",
                details=f"Empty order {order_number} deleted (no devices attached).",
            ))
            return jsonify({"message": f"Order {order_number} deleted."})

    @api_bp.route("/orders/<order_number>", methods=["PATCH"])
    def correct_order(order_number):
        payload = request.get_json(silent=True) or {}
        operator = (payload.get("operator") or "").strip() or "system"
        new_order_number = (payload.get("new_order_number") or "").strip() or None

        quantity = payload.get("quantity")
        if quantity is not None:
            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                return jsonify({"error": "quantity must be a whole number."}), 400

        if new_order_number is None and quantity is None:
            return jsonify({"error": "Provide new_order_number and/or quantity to update."}), 400

        db = DatabaseManager()

        try:
            with db.session() as db_session:
                order_service = OrderService(db_session)
                order = order_service.correct_order(
                    order_number,
                    new_order_number=new_order_number,
                    quantity=quantity,
                )

                changes = []
                if new_order_number:
                    changes.append(f"renamed to {new_order_number}")
                if quantity is not None:
                    changes.append(f"quantity set to {quantity}")

                audit_repo = AuditRepository(db_session)
                audit_repo.create(AuditLog(
                    operator=operator,
                    action="Order Corrected",
                    details=f"Order {order_number}: {', '.join(changes)}.",
                ))

                result_order_number = order.order_number
                result_quantity = order.quantity
        except ValueError as error:
            return jsonify({"error": str(error)}), 409
        except IntegrityError:
            return jsonify({
                "error": f"Could not update order {order_number} - the requested order number is already in use.",
            }), 409

        return jsonify({
            "message": f"Order {order_number} updated.",
            "order_number": result_order_number,
            "quantity": result_quantity,
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
            order_repo = OrderRepository(db_session)
            if order_repo.get_by_order_number(order_number) is None:
                return jsonify({"error": f"Order {order_number} does not exist."}), 404

        engine.start(operator, order_number)

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

    @api_bp.route("/workflow/mac-assign", methods=["PUT"])
    def workflow_mac_assign():
        if engine.state != WorkflowState.ASSIGNING_MAC:
            return jsonify({"error": "Not currently assigning MAC addresses"}), 409

        payload = request.get_json(silent=True) or {}
        mac1 = (payload.get("mac1") or "").strip()

        if not mac1:
            return jsonify({"error": "mac1 is required"}), 400

        db = DatabaseManager()
        with db.session() as db_session:
            mac_repo = MacAddressRepository(db_session)

            mac_entry_1 = mac_repo.get_by_mac(mac1)
            if mac_entry_1 is None or mac_entry_1.used:
                return jsonify({"error": f"MAC address {mac1} is not available."}), 409

            mac_entry_2 = mac_repo.get_next_available_excluding(mac1)
            if mac_entry_2 is None:
                return jsonify({"error": "No second MAC address available in the pool."}), 409

            mac2 = mac_entry_2.mac_address

        # Only validated here, not claimed - the pool entries aren't
        # marked used until the device is actually saved (see
        # DeviceService.record_result), so a cancelled session never
        # leaves MACs stuck in limbo.
        engine.set_mac_addresses(mac1, mac2)

        return workflow_response()

    @api_bp.route("/workflow/mac-confirm", methods=["POST"])
    def workflow_mac_confirm():
        if engine.state != WorkflowState.ASSIGNING_MAC:
            return jsonify({"error": "Not currently assigning MAC addresses"}), 409

        engine.confirm_mac_assignment()

        return workflow_response()

    @api_bp.route("/workflow/verify-confirm", methods=["POST"])
    def workflow_verify_confirm():
        if engine.state != WorkflowState.VERIFYING_MAC:
            return jsonify({"error": "Not currently verifying MAC addresses"}), 409

        engine.confirm_mac_verification()

        return workflow_response()
    
    @api_bp.route("/workflow/result", methods=["PUT"])
    def workflow_result():
        if engine.state != WorkflowState.AWAITING_RESULT:
            return jsonify({"error": "Complete all test steps before recording a result"}), 409

        payload = request.get_json(silent=True) or {}
        result = (payload.get("result") or "").strip().upper()
        notes = (payload.get("notes") or "").strip()

        if result not in ("PASS", "FAIL"):
            return jsonify({"error": "result must be PASS or FAIL"}), 400

        if result == "FAIL" and not notes:
            return jsonify({"error": "Notes are required when recording a failed test."}), 400

        engine.set_test_result(result, notes)

        return workflow_response()

    @api_bp.route("/workflow/serial", methods=["PUT"])
    def workflow_serial():
        if engine.state != WorkflowState.AWAITING_SERIAL:
            return jsonify({"error": "Not currently awaiting a serial number"}), 409

        payload = request.get_json(silent=True) or {}
        serial_number = (payload.get("serial_number") or "").strip()

        if not is_valid_serial_number(serial_number):
            return jsonify({"error": "Serial number must be formatted as EMyyww0000."}), 400

        db = DatabaseManager()
        with db.session() as db_session:
            device_repo = DeviceRepository(db_session)
            existing = device_repo.get_by_order_and_serial(
                engine.session.order_number, serial_number
            )
            if existing is not None:
                return jsonify({
                    "error": f"Serial {serial_number} already exists for this order.",
                }), 409

        engine.set_serial_number(serial_number)

        return workflow_response()

    @api_bp.route("/session/finish", methods=["POST"])
    def session_finish():
        if engine.state != WorkflowState.READY_TO_SAVE:
            return jsonify({"error": "Session is not ready to be saved"}), 409

        session = engine.session
        db = DatabaseManager()

        try:
            with db.session() as db_session:
                if session.test_result == "PASS":
                    device_service = DeviceService(db_session)
                    device_service.record_pass(
                        order_number=session.order_number,
                        serial_number=session.serial_number,
                        operator=session.operator,
                        mac1=session.mac1,
                    )
                else:
                    order_service = OrderService(db_session)
                    order_service.record_failure(
                        order_number=session.order_number,
                        operator=session.operator,
                        reason=session.test_notes,
                    )

                    audit_repo = AuditRepository(db_session)
                    audit_repo.create(AuditLog(
                        operator=session.operator or "unknown",
                        action="Test Failed",
                        details=(
                            f"Order {session.order_number} - failed testing. "
                            f"Notes: {session.test_notes}"
                        ),
                    ))

                maybe_export_completed_order(db_session, application, session.order_number)
        except ValueError as error:
            return jsonify({"error": str(error)}), 409

        engine.restart()

        step = build_step_payload(engine, qr_service)

        return jsonify({
            "session": session_dict(engine.session, engine.state),
            "step": step, "message": "Saved.",
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
        order_number = (request.args.get("order_number") or "").strip() or None

        db = DatabaseManager()

        with db.session() as db_session:
            repo = DeviceRepository(db_session)

            if order_number:
                device = repo.get_by_order_and_serial(order_number, serial)
                if device is None:
                    return jsonify({"error": "Device not found"}), 404
                return jsonify({"device": device_dict(device)})

            matches = repo.list_by_serial(serial)

            if not matches:
                return jsonify({"error": "Device not found"}), 404

            if len(matches) > 1:
                return jsonify({
                    "candidates": [device_dict(d) for d in matches],
                })

            return jsonify({"device": device_dict(matches[0])})

    @api_bp.route("/devices/<serial>", methods=["PUT"])
    def update_device(serial):
        payload = request.get_json(silent=True) or {}

        current_order_number = (payload.get("current_order_number") or "").strip() or None
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
            return jsonify({"error": "Serial number must be formatted as EMyyww0000."}), 400

        db = DatabaseManager()

        with db.session() as db_session:
            repo = DeviceRepository(db_session)
            device, error = resolve_device_by_serial(repo, serial, current_order_number)
            if error is not None:
                body, status = error
                return jsonify(body), status

            # MAC fields only make sense on a device that has actually
            # passed - a FAIL is never supposed to hold MAC addresses.
            # Assigning MACs for the first time goes through the normal
            # PASS workflow, not this manual-correction endpoint.

            conflict = repo.get_by_order_and_serial(order_number, new_serial)
            if conflict is not None and conflict.id != device.id:
                return jsonify({"error": "Serial number already exists for that order."}), 409

            before = device_dict(device)

            old_mac1, old_mac2 = device.ethaddr_id, device.eth1addr_id
            new_mac1 = mac1 or None
            new_mac2 = mac2 or None

            if old_mac1 != new_mac1 or old_mac2 != new_mac2:
                mac_repo = MacAddressRepository(db_session)
                new_macs = {new_mac1, new_mac2}

                for candidate in (new_mac1, new_mac2):
                    if not candidate:
                        continue
                    # The MAC must actually be a registered pool address -
                    # previously this wasn't checked, letting the devices
                    # table and the pool silently drift out of sync.
                    if mac_repo.get_by_mac(candidate) is None:
                        return jsonify({"error": f"MAC address {candidate} is not in the MAC pool."}), 400

                    conflict = repo.get_by_single_mac(candidate)
                    if conflict is not None and conflict.id != device.id:
                        return jsonify({"error": f"MAC address {candidate} is already assigned to another device."}), 409

                for old_mac in (old_mac1, old_mac2):
                    if old_mac and old_mac not in new_macs:
                        old_entry = mac_repo.get_by_mac(old_mac)
                        if old_entry is not None:
                            mac_repo.mark_unused(old_entry)

                for claimed_mac in (new_mac1, new_mac2):
                    if claimed_mac:
                        claimed_entry = mac_repo.get_by_mac(claimed_mac)
                        if claimed_entry is not None:
                            mac_repo.mark_used(claimed_entry)

            device.order_number = order_number
            device.serial_number = new_serial
            device.operator = operator
            device.ethaddr_id = new_mac1
            device.eth1addr_id = new_mac2
            device.used = device.test_result == "PASS"

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
        current_order_number = (payload.get("current_order_number") or "").strip() or None

        if not reason:
            return jsonify({"error": "A reason is required to reset a MAC address."}), 400

        db = DatabaseManager()

        with db.session() as db_session:
            repo = DeviceRepository(db_session)
            device, error = resolve_device_by_serial(repo, serial, current_order_number)
            if error is not None:
                body, status = error
                return jsonify(body), status

            # Releases the MAC pair back to the pool and removes the
            # device entirely - there's no "failed" state for a device
            # row to fall back into anymore, so undoing a pass means
            # undoing the whole record. The board re-enters the line as
            # a fresh test with a new serial if retested.
            mac_repo = MacAddressRepository(db_session)
            for mac_value in (device.ethaddr_id, device.eth1addr_id):
                if not mac_value:
                    continue
                mac_entry = mac_repo.get_by_mac(mac_value)
                if mac_entry is not None:
                    mac_repo.mark_unused(mac_entry)

            audit_repo = AuditRepository(db_session)
            audit_repo.create(AuditLog(
                operator=device.operator or "unknown",
                action="MAC Reset",
                details=f"Device {device.serial_number} removed and MAC addresses released. Reason: {reason}",
            ))

            repo.delete(device)

            return jsonify({
                "message": "Device removed and MAC addresses released.",
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
