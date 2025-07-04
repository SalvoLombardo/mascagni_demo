# config.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Valori comuni a tutti gli ambienti."""
    # chiave di sessione (sovrascrivibile via env var)
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

    # DB: se trovi DATABASE_URL la usi, altrimenti un SQLite locale
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🔑 flag demo (true/false, di default false)
    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


class DevelopmentConfig(Config):
    """Impostazioni che usi in locale."""
    DEBUG = True
    # se non hai DATABASE_URL, usa il tuo Postgres locale
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres@localhost:5432/mascagni_db"
    )


class ProductionConfig(Config):
    DEBUG = False