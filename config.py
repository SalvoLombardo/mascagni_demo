import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Valori comuni a tutti gli ambienti."""

    # Chiave di sessione (può essere sovrascritta via variabile d'ambiente)
    SECRET_KEY = os.getenv("SECRET_KEY", "insert-your-secret-key")

    # Connessione al database
    @staticmethod
    def get_database_uri():
        database_url = os.getenv("DATABASE_URL")
        if database_url and database_url.startswith("postgres://"):
            # Converti postgres:// in postgresql:// per compatibilità SQLAlchemy
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        # Fallback su SQLite locale se DATABASE_URL non è impostato
        return database_url or f"sqlite:///{BASE_DIR / 'app.db'}"

    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flag demo (true/false, di default false)
    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


class DevelopmentConfig(Config):
    """Impostazioni per l'ambiente di sviluppo locale."""
    DEBUG = True
    # Fallback locale per Postgres in caso DATABASE_URL non sia impostato
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres@localhost:5432/mascagni_db"
    )


class ProductionConfig(Config):
    """Impostazioni per l'ambiente di produzione."""
    DEBUG = False