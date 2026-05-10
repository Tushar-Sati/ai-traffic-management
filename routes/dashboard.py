import json
from pathlib import Path

from flask import Blueprint, current_app, jsonify, render_template

from db import db_cursor
from routes.auth import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total FROM traffic_records")
        total_records = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(*) AS total FROM traffic_records WHERE accident='High Risk'")
        high_risk = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(*) AS total FROM alerts WHERE is_active=1")
        active_alerts = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(DISTINCT location) AS total FROM traffic_records WHERE accident='High Risk'")
        hotspots = cur.fetchone()["total"]
        cur.execute("SELECT AVG(traffic_density) AS avg_density FROM traffic_records")
        avg_density = cur.fetchone()["avg_density"] or 0
        cur.execute("SELECT AVG(speed) AS avg_speed FROM traffic_records")
        avg_speed = cur.fetchone()["avg_speed"] or 0
        cur.execute("""
            SELECT location, COUNT(*) AS incidents, AVG(traffic_density) AS avg_density,
                   CASE
                       WHEN SUM(accident = 'High Risk') > 0 THEN 'High Risk'
                       WHEN SUM(accident = 'Medium Risk') > 0 THEN 'Medium Risk'
                       ELSE 'Low Risk'
                   END AS risk_level
            FROM traffic_records
            WHERE accident IN ('High Risk', 'Medium Risk')
            GROUP BY location
            ORDER BY incidents DESC, avg_density DESC
            LIMIT 6
        """)
        hotspot_rows = cur.fetchall()
        cur.execute("""
            SELECT id, date, time, location, weather, traffic_density, vehicle_count, speed,
                   road_condition, accident
            FROM traffic_records
            ORDER BY date DESC, time DESC
            LIMIT 8
        """)
        recent_records = cur.fetchall()
        cur.execute("""
            SELECT id, location, risk_level, message, created_at
            FROM alerts WHERE is_active=1 ORDER BY created_at DESC LIMIT 5
        """)
        alerts = cur.fetchall()
    high_risk_rate = round((high_risk / total_records) * 100, 1) if total_records else 0
    model_path = Path(current_app.config["MODEL_PATH"])
    model_ready = model_path.exists()
    metrics_path = model_path.with_name("metrics.json")
    model_metrics = {}
    if metrics_path.exists():
        model_metrics = json.loads(metrics_path.read_text())
    return render_template(
        "dashboard.html",
        total_records=total_records,
        total_accidents=high_risk,
        active_alerts=active_alerts,
        hotspots=hotspots,
        traffic_density=round(float(avg_density), 2),
        avg_speed=round(float(avg_speed), 2),
        high_risk_rate=high_risk_rate,
        hotspot_rows=hotspot_rows,
        recent_records=recent_records,
        alerts=alerts,
        model_ready=model_ready,
        model_metrics=model_metrics,
    )


@dashboard_bp.route("/api/analytics")
@login_required
def analytics():
    with db_cursor() as cur:
        cur.execute("""
            SELECT DATE_FORMAT(date, '%Y-%m-%d') AS label, COUNT(*) AS total
            FROM traffic_records WHERE accident='High Risk'
            GROUP BY date ORDER BY date DESC LIMIT 14
        """)
        daily = list(reversed(cur.fetchall()))
        cur.execute("""
            SELECT DATE_FORMAT(date, '%Y-%m') AS label, COUNT(*) AS total
            FROM traffic_records WHERE accident='High Risk'
            GROUP BY DATE_FORMAT(date, '%Y-%m') ORDER BY label DESC LIMIT 12
        """)
        monthly = list(reversed(cur.fetchall()))
        cur.execute("""
            SELECT accident AS label, COUNT(*) AS total
            FROM traffic_records
            GROUP BY accident
            ORDER BY FIELD(accident, 'High Risk', 'Medium Risk', 'Low Risk')
        """)
        risk_mix = cur.fetchall()
        cur.execute("""
            SELECT weather AS label, COUNT(*) AS total
            FROM traffic_records
            GROUP BY weather
            ORDER BY total DESC
        """)
        weather = cur.fetchall()
        cur.execute("""
            SELECT road_condition AS label, COUNT(*) AS total
            FROM traffic_records
            GROUP BY road_condition
            ORDER BY total DESC
        """)
        roads = cur.fetchall()
    return jsonify({"daily": daily, "monthly": monthly, "risk_mix": risk_mix, "weather": weather, "roads": roads})
