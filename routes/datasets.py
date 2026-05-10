import pandas as pd
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from db import db_cursor
from routes.auth import login_required

datasets_bp = Blueprint("datasets", __name__, url_prefix="/datasets")

REQUIRED_COLUMNS = [
    "date", "time", "location", "lat", "lng", "weather", "traffic_density",
    "vehicle_count", "speed", "road_condition", "accident"
]


def normalize_risk(value):
    text = str(value).strip().lower()
    if text in {"high", "high risk", "1", "yes", "true"}:
        return "High Risk"
    if text in {"medium", "medium risk"}:
        return "Medium Risk"
    return "Low Risk"


@datasets_bp.route("")
@login_required
def list_records():
    with db_cursor() as cur:
        cur.execute("SELECT * FROM traffic_records ORDER BY date DESC, time DESC LIMIT 300")
        records = cur.fetchall()
    return render_template("datasets.html", records=records, record=None, columns=REQUIRED_COLUMNS)


@datasets_bp.route("/create", methods=["POST"])
@login_required
def create_record():
    data = {key: request.form.get(key, "").strip() for key in REQUIRED_COLUMNS}
    data["accident"] = normalize_risk(data["accident"])
    try:
        insert_record(data)
        flash("Record added.", "success")
    except Exception:
        current_app.logger.exception("Could not add traffic record.")
        flash("Could not add record. Please check the data and try again.", "danger")
    return redirect(url_for("datasets.list_records"))


@datasets_bp.route("/edit/<int:record_id>")
@login_required
def edit_record(record_id):
    with db_cursor() as cur:
        cur.execute("SELECT * FROM traffic_records WHERE id=%s", (record_id,))
        record = cur.fetchone()
        cur.execute("SELECT * FROM traffic_records ORDER BY date DESC, time DESC LIMIT 300")
        records = cur.fetchall()
    return render_template("datasets.html", records=records, record=record, columns=REQUIRED_COLUMNS)


@datasets_bp.route("/update/<int:record_id>", methods=["POST"])
@login_required
def update_record(record_id):
    data = {key: request.form.get(key, "").strip() for key in REQUIRED_COLUMNS}
    data["accident"] = normalize_risk(data["accident"])
    try:
        with db_cursor(commit=True) as cur:
            cur.execute("""
                UPDATE traffic_records
                SET date=%s, time=%s, location=%s, lat=%s, lng=%s, weather=%s,
                    traffic_density=%s, vehicle_count=%s, speed=%s, road_condition=%s, accident=%s
                WHERE id=%s
            """, tuple(data[c] for c in REQUIRED_COLUMNS) + (record_id,))
        flash("Record updated.", "success")
    except Exception:
        current_app.logger.exception("Could not update traffic record.")
        flash("Could not update record. Please check the data and try again.", "danger")
    return redirect(url_for("datasets.list_records"))


@datasets_bp.route("/delete/<int:record_id>", methods=["POST"])
@login_required
def delete_record(record_id):
    with db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM traffic_records WHERE id=%s", (record_id,))
    flash("Record deleted.", "success")
    return redirect(url_for("datasets.list_records"))


@datasets_bp.route("/upload", methods=["POST"])
@login_required
def upload_csv():
    file = request.files.get("csv_file")
    if not file or not file.filename.lower().endswith(".csv"):
        flash("Please upload a CSV file.", "warning")
        return redirect(url_for("datasets.list_records"))
    try:
        df = pd.read_csv(file)
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            flash(f"Missing columns: {', '.join(missing)}", "danger")
            return redirect(url_for("datasets.list_records"))
        count = 0
        for _, row in df[REQUIRED_COLUMNS].dropna().iterrows():
            data = {col: row[col] for col in REQUIRED_COLUMNS}
            data["accident"] = normalize_risk(data["accident"])
            insert_record(data)
            count += 1
        flash(f"Imported {count} records.", "success")
    except Exception:
        current_app.logger.exception("Could not import traffic CSV.")
        flash("Upload failed. Please check the CSV file and try again.", "danger")
    return redirect(url_for("datasets.list_records"))


def insert_record(data):
    with db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO traffic_records
            (date, time, location, lat, lng, weather, traffic_density, vehicle_count, speed, road_condition, accident)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, tuple(data[c] for c in REQUIRED_COLUMNS))
