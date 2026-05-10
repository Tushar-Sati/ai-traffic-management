from pathlib import Path

from flask import Flask
from werkzeug.security import generate_password_hash

from config import Config
from db import db_cursor
from routes.alerts import alerts_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.datasets import datasets_bp
from routes.map_routes import map_bp
from routes.ml import ml_bp
from routes.reports import reports_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["MODEL_PATH"]).parent.mkdir(parents=True, exist_ok=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(datasets_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(reports_bp)

    with app.app_context():
        seed_admin()

    return app


def seed_admin():
    try:
        with db_cursor(commit=True) as cur:
            cur.execute("SELECT id FROM admins WHERE username=%s", ("admin",))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO admins (username, password_hash) VALUES (%s, %s)",
                    ("admin", generate_password_hash("admin123")),
                )
    except Exception as exc:
        print(f"Database not ready: {exc}")


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
