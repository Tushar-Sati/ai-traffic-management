import joblib
import pandas as pd
from flask import Blueprint, current_app, jsonify, render_template, request

from db import db_cursor
from routes.auth import login_required

ml_bp = Blueprint("ml", __name__)


@ml_bp.route("/prediction")
@login_required
def prediction_page():
    return render_template("prediction.html")


@ml_bp.route("/api/predict", methods=["POST"])
@login_required
def predict():
    payload = request.get_json(silent=True) or {}
    required = ["traffic_density", "weather", "vehicle_count", "speed", "road_condition"]
    missing = [key for key in required if payload.get(key) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        model = joblib.load(current_app.config["MODEL_PATH"])
    except Exception:
        return jsonify({"error": "Model not found. Run python train_model.py first."}), 500

    frame = pd.DataFrame([{
        "traffic_density": float(payload["traffic_density"]),
        "weather": str(payload["weather"]),
        "vehicle_count": int(payload["vehicle_count"]),
        "speed": float(payload["speed"]),
        "road_condition": str(payload["road_condition"]),
    }])
    risk = model.predict(frame)[0]
    probabilities = dict(zip(model.classes_, model.predict_proba(frame)[0]))
    probability = round(float(probabilities.get(risk, 0)) * 100, 2)
    recommendation = recommendation_for(risk)

    if risk == "High Risk" and not current_app.config["DEMO_MODE"]:
        try:
            with db_cursor(commit=True) as cur:
                cur.execute("""
                    INSERT INTO alerts (location, risk_level, message)
                    VALUES (%s, %s, %s)
                """, (payload.get("location", "Prediction Form"), risk, recommendation))
        except Exception:
            current_app.logger.exception("Could not store prediction alert.")

    return jsonify({"risk_level": risk, "probability": probability, "recommendation": recommendation})


def recommendation_for(risk):
    if risk == "High Risk":
        return "Deploy traffic police, lower speed limits, and notify nearby emergency response teams."
    if risk == "Medium Risk":
        return "Monitor congestion, adjust signals, and warn drivers to reduce speed."
    return "Traffic conditions are stable. Continue routine monitoring."
