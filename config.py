import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "traffic_ai")
    DB_CONNECTION_TIMEOUT = int(os.getenv("DB_CONNECTION_TIMEOUT", "3"))
    DEMO_MODE = os.getenv("DEMO_MODE", "").lower() in {"1", "true", "yes"} or (
        os.getenv("VERCEL") == "1" and DB_HOST in {"localhost", "127.0.0.1"}
    )
    UPLOAD_FOLDER = BASE_DIR / "dataset" / "uploads"
    MODEL_PATH = BASE_DIR / "models" / "best_model.pkl"
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
