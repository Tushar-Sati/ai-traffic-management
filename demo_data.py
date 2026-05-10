import csv
from collections import Counter, defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DATA = BASE_DIR / "dataset" / "sample_traffic_data.csv"


def traffic_records(limit=None):
    with SAMPLE_DATA.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    records = [normalize_record(row, index + 1) for index, row in enumerate(rows)]
    records.sort(key=lambda row: (row["date"], row["time"]), reverse=True)
    return records[:limit] if limit else records


def normalize_record(row, record_id):
    record = dict(row)
    record["id"] = record_id
    record["lat"] = float(record["lat"])
    record["lng"] = float(record["lng"])
    record["traffic_density"] = float(record["traffic_density"])
    record["vehicle_count"] = int(float(record["vehicle_count"]))
    record["speed"] = float(record["speed"])
    return record


def active_alerts(limit=None):
    alerts = []
    for record in traffic_records():
        if record["accident"] == "High Risk":
            alerts.append({
                "id": record["id"],
                "location": record["location"],
                "risk_level": record["accident"],
                "message": "High accident risk detected. Review signal timing and dispatch support.",
                "created_at": f"{record['date']} {record['time']}",
                "is_active": 1,
            })
    return alerts[:limit] if limit else alerts


def dashboard_summary():
    records = traffic_records()
    high_risk = [row for row in records if row["accident"] == "High Risk"]
    elevated = [row for row in records if row["accident"] in {"High Risk", "Medium Risk"}]
    grouped = defaultdict(list)
    for row in elevated:
        grouped[row["location"]].append(row)

    hotspot_rows = []
    for location, rows in grouped.items():
        risk_level = "High Risk" if any(row["accident"] == "High Risk" for row in rows) else "Medium Risk"
        hotspot_rows.append({
            "location": location,
            "incidents": len(rows),
            "avg_density": sum(row["traffic_density"] for row in rows) / len(rows),
            "risk_level": risk_level,
        })
    hotspot_rows.sort(key=lambda row: (row["incidents"], row["avg_density"]), reverse=True)

    return {
        "total_records": len(records),
        "total_accidents": len(high_risk),
        "active_alerts": len(active_alerts()),
        "hotspots": len({row["location"] for row in high_risk}),
        "traffic_density": round(sum(row["traffic_density"] for row in records) / len(records), 2),
        "avg_speed": round(sum(row["speed"] for row in records) / len(records), 2),
        "high_risk_rate": round((len(high_risk) / len(records)) * 100, 1) if records else 0,
        "hotspot_rows": hotspot_rows[:6],
        "recent_records": records[:8],
        "alerts": active_alerts(limit=5),
    }


def analytics():
    records = traffic_records()
    high_risk = [row for row in records if row["accident"] == "High Risk"]
    daily_counts = Counter(row["date"] for row in high_risk)
    monthly_counts = Counter(row["date"][:7] for row in high_risk)
    risk_counts = Counter(row["accident"] for row in records)
    weather_counts = Counter(row["weather"] for row in records)
    road_counts = Counter(row["road_condition"] for row in records)

    return {
        "daily": series(daily_counts),
        "monthly": series(monthly_counts),
        "risk_mix": [{"label": label, "total": risk_counts.get(label, 0)} for label in ["High Risk", "Medium Risk", "Low Risk"]],
        "weather": series(weather_counts, sort_by_count=True),
        "roads": series(road_counts, sort_by_count=True),
    }


def series(counter, sort_by_count=False):
    items = counter.items()
    if sort_by_count:
        items = sorted(items, key=lambda item: item[1], reverse=True)
    else:
        items = sorted(items)
    return [{"label": label, "total": total} for label, total in items]
