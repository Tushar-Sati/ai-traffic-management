import csv
from io import BytesIO, StringIO

from flask import Blueprint, Response, current_app, render_template, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import demo_data
from db import db_cursor
from routes.auth import login_required

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("")
@login_required
def reports_page():
    return render_template("reports.html")


@reports_bp.route("/export/csv")
@login_required
def export_csv():
    rows = fetch_records()
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys() if rows else ["message"])
    writer.writeheader()
    writer.writerows(rows or [{"message": "No records available"}])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=traffic_report.csv"},
    )


@reports_bp.route("/export/pdf")
@login_required
def export_pdf():
    rows = fetch_records(limit=40)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "AI Traffic Management Report")
    y -= 30
    pdf.setFont("Helvetica", 9)
    for row in rows:
        line = f"{row['date']} {row['time']} | {row['location']} | {row['weather']} | {row['accident']}"
        pdf.drawString(40, y, line[:110])
        y -= 16
        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = height - 50
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="traffic_report.pdf", mimetype="application/pdf")


def fetch_records(limit=None):
    if current_app.config["DEMO_MODE"]:
        return demo_data.traffic_records(limit=limit)
    sql = "SELECT date, time, location, weather, traffic_density, vehicle_count, speed, road_condition, accident FROM traffic_records ORDER BY date DESC, time DESC"
    if limit:
        sql += " LIMIT %s"
    try:
        with db_cursor() as cur:
            cur.execute(sql, (limit,) if limit else None)
            return cur.fetchall()
    except Exception:
        current_app.logger.exception("Report database query failed. Using demo data.")
        return demo_data.traffic_records(limit=limit)
