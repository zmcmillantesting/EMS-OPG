from datetime import UTC, datetime

from flask import Blueprint, jsonify, request

from ems_opg.core.constants import APP_VERSION
from ems_opg.database.database import DatabaseManager
from ems_opg.database.models import Device
from ems_opg.services.device_service import DeviceService
from ems_opg.services.qr_service import QRService
from ems_opg.workflow.workflow_engine import WorkflowEngine
from ems_opg.workflow.workflow_state import WorkflowState


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
                    ethaddr1_id=engine.session.mac2,
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

    app.register_blueprint(api_bp)
