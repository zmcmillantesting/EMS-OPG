from flask import Flask, send_from_directory

from ems_opg.api.routes import register_routes


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

    register_routes(app, application)

    return app
