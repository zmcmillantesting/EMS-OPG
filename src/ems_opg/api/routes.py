from datetime import UTC, datetime
import logging, shutil
from flask import Blueprint, jsonify, request

from ems_opg.core.constants import APP_VERSION
from ems_opg.database.database import DatabaseManager
from ems_opg.database.engine import DATABASE_FILE
from ems_opg.database.models import Device
from ems_opg.services.device_service import DeviceService
from ems_opg.services.order_service import OrderService
from ems_opg.services.qr_service import QRService
from ems_opg.workflow.workflow_engine import WorkflowEngine
from ems_opg.workflow.workflow_state import WorkflowState

LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}

def session_dict(session):
    return {
        "operator": session.operator,
        "order_number": session.order_number,
        "serial_number": session.serial_number,
        "mac1": session.mac1,
        "mac2": session.mac2,
        "current_step": session.current_step,
        "total_steps": session.total_steps,
        "completed": session.completed,
        "cancelled": session.cancelled,
    }


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

        return jsonify({"message": result["message"]}), 201

    @api_bp.route("/session/start", methods=["POST"])
    def session_start():
        payload = request.get_json(silent=True) or {}
        operator = (payload.get("operator") or "").strip()
        order_number = (payload.get("order_number") or "").strip()

        if not operator or not order_number:
            return jsonify({"error": "operator and order_number are required"}), 400

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

    @api_bp.route("/session/finish", methods=["POST"])
    def session_finish():
        if not session_active():
            return jsonify({"error": "No active session"}), 404

        payload = request.get_json(silent=True) or {}
        serial_number = (payload.get("serial_number") or "").strip()

        if not serial_number:
            return jsonify({"error": "serial_number is required"}), 400

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
                )
        except ValueError as error:
            return jsonify({"error": str(error)}), 409

        engine.finish(serial_number)

        return jsonify({
            "session": session_dict(engine.session),
            "message": "Device saved to traceability log.",
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

        if not source.exists():
            return jsonify({"error": "No database file found to back up"}), 404

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        destination = application.paths.backup_dir / f"ems_opg_{timestamp}.db"

        shutil.copy2(source, destination)

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

    @api_bp.route("/api/devices", methods=["GET"])
    def api_devices_get():
        pass

    @api_bp.route("/api/devices/:serial", methods=["PUT"])
    def set_api_device_serial():
        pass

    @api_bp.route("/api/devices/:serial/reset-mac", methods=["POST"])
    def api_reset_macs():
        pass

    @api_bp.route("/api/mac/:mac", methods=["GET"])
    def get_api_mac():
        pass

    @api_bp.route("/api/history?q=", methods=["GET"])
    def get_api_history():
        pass

    @api_bp.route("/api/history/export", methods=["GET"])
    def get_api_history():
        pass

    app.register_blueprint(api_bp)
