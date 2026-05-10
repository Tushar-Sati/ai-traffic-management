from flask import Blueprint, current_app, jsonify, render_template

import demo_data
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
    if current_app.config["DEMO_MODE"]:
        points = [
            {
                "location": row["location"],
                "lat": row["lat"],
                "lng": row["lng"],
                "risk_level": row["accident"],
                "traffic_density": row["traffic_density"],
                "vehicle_count": row["vehicle_count"],
            }
            for row in demo_data.traffic_records(limit=500)
        ]
    else:
        try:
            with db_cursor() as cur:
                cur.execute("""
                    SELECT location, lat, lng, accident AS risk_level, traffic_density, vehicle_count
                    FROM traffic_records
                    WHERE lat IS NOT NULL AND lng IS NOT NULL
                    ORDER BY date DESC, time DESC LIMIT 500
                """)
                points = cur.fetchall()
        except Exception:
            current_app.logger.exception("Map database query failed. Using demo data.")
            points = [
                {
                    "location": row["location"],
                    "lat": row["lat"],
                    "lng": row["lng"],
                    "risk_level": row["accident"],
                    "traffic_density": row["traffic_density"],
                    "vehicle_count": row["vehicle_count"],
                }
                for row in demo_data.traffic_records(limit=500)
            ]
    return jsonify(points)
