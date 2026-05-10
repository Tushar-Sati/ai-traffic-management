import json
from pathlib import Path

import joblib
import mysql.connector
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from config import Config

FEATURES = ["traffic_density", "weather", "vehicle_count", "speed", "road_condition"]
TARGET = "accident"


def load_data():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
        )
        df = pd.read_sql("SELECT traffic_density, weather, vehicle_count, speed, road_condition, accident FROM traffic_records", conn)
        conn.close()
        if len(df) >= 10:
            return df
    except Exception as exc:
        print(f"Database load skipped: {exc}")
    sample_path = Path(__file__).resolve().parent / "dataset" / "sample_traffic_data.csv"
    return pd.read_csv(sample_path)


def build_pipeline(model):
    numeric_features = ["traffic_density", "vehicle_count", "speed"]
    categorical_features = ["weather", "road_condition"]
    preprocess = ColumnTransformer([
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ])
    return Pipeline([("preprocess", preprocess), ("model", model)])


def main():
    df = load_data().dropna(subset=FEATURES + [TARGET])
    if df.empty:
        raise RuntimeError("No training data available.")
    if df[TARGET].astype(str).nunique() < 2:
        sample_path = Path(__file__).resolve().parent / "dataset" / "sample_traffic_data.csv"
        df = pd.concat([df, pd.read_csv(sample_path)], ignore_index=True)
    X = df[FEATURES]
    y = df[TARGET].astype(str)
    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=stratify)

    candidates = {
        "RandomForest": RandomForestClassifier(n_estimators=160, random_state=42, class_weight="balanced"),
        "LogisticRegression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "DecisionTree": DecisionTreeClassifier(random_state=42, class_weight="balanced"),
    }

    scores = {}
    best_name, best_pipeline, best_score = None, None, -1
    for name, model in candidates.items():
        pipeline = build_pipeline(model)
        pipeline.fit(X_train, y_train)
        score = accuracy_score(y_test, pipeline.predict(X_test))
        scores[name] = round(score, 4)
        if score > best_score:
            best_name, best_pipeline, best_score = name, pipeline, score

    Path(Config.MODEL_PATH).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, Config.MODEL_PATH)
    metrics_path = Path(Config.MODEL_PATH).with_name("metrics.json")
    metrics_path.write_text(
        json.dumps(
            {
                "best_model": best_name,
                "best_accuracy": round(best_score, 4),
                "accuracy_comparison": scores,
                "training_rows": int(len(df)),
                "features": FEATURES,
            },
            indent=2,
        )
    )
    print("Accuracy comparison:", scores)
    print(f"Saved best model: {best_name} ({best_score:.4f}) -> {Config.MODEL_PATH}")


if __name__ == "__main__":
    main()
