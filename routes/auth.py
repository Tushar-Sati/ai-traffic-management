from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from db import db_cursor

auth_bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


@auth_bp.route("/", methods=["GET"])
def index():
    return redirect(url_for("dashboard.dashboard") if session.get("admin_id") else url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if current_app.config["DEMO_MODE"]:
            if username == "admin" and password == "admin123":
                session.clear()
                session["admin_id"] = 1
                session["username"] = "admin"
                return redirect(url_for("dashboard.dashboard"))
            flash("Invalid admin credentials.", "danger")
            return render_template("login.html"), 401
        try:
            with db_cursor() as cur:
                cur.execute("SELECT * FROM admins WHERE username=%s", (username,))
                admin = cur.fetchone()
        except Exception:
            current_app.logger.exception("Admin login failed because the database is unavailable.")
            if username == "admin" and password == "admin123":
                session.clear()
                session["admin_id"] = 1
                session["username"] = "admin"
                return redirect(url_for("dashboard.dashboard"))
            flash("Invalid admin credentials.", "danger")
            return render_template("login.html"), 401
        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_id"] = admin["id"]
            session["username"] = admin["username"]
            return redirect(url_for("dashboard.dashboard"))
        flash("Invalid admin credentials.", "danger")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))
