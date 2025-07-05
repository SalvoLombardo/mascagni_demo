import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Valori comuni a tutti gli ambienti."""

    SECRET_KEY = os.getenv("SECRET_KEY", "insert-your-secret-key")

    @staticmethod
    def get_database_uri():
        database_url = os.getenv("DATABASE_URL")
        if database_url and database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url or f"sqlite:///{BASE_DIR / 'app.db'}"

    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


class DevelopmentConfig(Config):
    """Impostazioni che usi in locale."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres@localhost:5432/mascagni_db"
    )


class ProductionConfig(Config):
    DEBUG = False