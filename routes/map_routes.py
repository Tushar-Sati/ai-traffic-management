from flask import Blueprint, jsonify, render_template

from db import db_cursor
from routes.auth import login_required

map_bp = Blueprint("map", __name__)


@map_bp.route("/map")
@login_required
def map_page():
    return render_template("map.html")


@map_bp.route("/api/map-points")
@login_required
def map_points():
    with db_cursor() as cur:
        cur.execute("""
            SELECT location, lat, lng, accident AS risk_level, traffic_density, vehicle_count
            FROM traffic_records
            WHERE lat IS NOT NULL AND lng IS NOT NULL
            ORDER BY date DESC, time DESC LIMIT 500
        """)
        points = cur.fetchall()
    return jsonify(points)
