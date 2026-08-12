from flask import Flask, Response, request, send_from_directory

from ems_opg.api.routes import register_routes

LOG_LEVEL_SEVERITY = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}


def create_app(application):
    frontend_dir = application.paths.root / "frontend"

    app = Flask(
        __name__,
        static_folder=str(frontend_dir),
        static_url_path="",
    )

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    @app.route("/qr/<path:filename>")
    def qr_image(filename):
        return send_from_directory(application.paths.qr_cache, filename)

    @app.route("/logs/<path:filename>")
    def log_file(filename):
        level = (request.args.get("level") or "").strip().upper()

        if level not in LOG_LEVEL_SEVERITY:
            return send_from_directory(
                application.paths.logs_dir,
                filename,
                mimetype="text/plain",
            )

        log_path = application.paths.logs_dir / filename
        if not log_path.exists():
            return Response("", mimetype="text/plain")

        minimum = LOG_LEVEL_SEVERITY[level]
        filtered_lines = []
        keep_current = True

        with open(log_path, "r", encoding="utf-8", errors="replace") as log:
            for line in log:
                parts = line.split("|", 2)
                if len(parts) >= 3 and parts[1].strip() in LOG_LEVEL_SEVERITY:
                    keep_current = LOG_LEVEL_SEVERITY[parts[1].strip()] >= minimum
                if keep_current:
                    filtered_lines.append(line)

        return Response("".join(filtered_lines), mimetype="text/plain")

    
            

    register_routes(app, application)

    return app
