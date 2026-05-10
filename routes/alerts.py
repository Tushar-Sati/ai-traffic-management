from flask import Blueprint, current_app, flash, redirect, render_template, url_for

import demo_data
from db import db_cursor
from routes.auth import login_required

alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")


@alerts_bp.route("")
@login_required
def list_alerts():
    if current_app.config["DEMO_MODE"]:
        alerts = demo_data.active_alerts()
    else:
        try:
            with db_cursor() as cur:
                cur.execute("SELECT * FROM alerts ORDER BY created_at DESC")
                alerts = cur.fetchall()
        except Exception:
            current_app.logger.exception("Alerts database query failed. Using demo data.")
            alerts = demo_data.active_alerts()
    return render_template("alerts.html", alerts=alerts)


@alerts_bp.route("/resolve/<int:alert_id>", methods=["POST"])
@login_required
def resolve_alert(alert_id):
    try:
        with db_cursor(commit=True) as cur:
            cur.execute("UPDATE alerts SET is_active=0 WHERE id=%s", (alert_id,))
        flash("Alert resolved.", "success")
    except Exception:
        current_app.logger.exception("Could not resolve alert.")
        flash("Alert updates require a connected database.", "warning")
    return redirect(url_for("alerts.list_alerts"))
