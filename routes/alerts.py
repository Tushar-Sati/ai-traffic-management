from flask import Blueprint, flash, redirect, render_template, url_for

from db import db_cursor
from routes.auth import login_required

alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")


@alerts_bp.route("")
@login_required
def list_alerts():
    with db_cursor() as cur:
        cur.execute("SELECT * FROM alerts ORDER BY created_at DESC")
        alerts = cur.fetchall()
    return render_template("alerts.html", alerts=alerts)


@alerts_bp.route("/resolve/<int:alert_id>", methods=["POST"])
@login_required
def resolve_alert(alert_id):
    with db_cursor(commit=True) as cur:
        cur.execute("UPDATE alerts SET is_active=0 WHERE id=%s", (alert_id,))
    flash("Alert resolved.", "success")
    return redirect(url_for("alerts.list_alerts"))
