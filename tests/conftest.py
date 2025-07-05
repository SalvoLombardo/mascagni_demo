import pytest
from app import create_app, db

@pytest.fixture
def app():
    # passiamo subito il dict di configurazione di test
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",   # DB in memoria
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        db.create_all()        # crea le tabelle sul DB di test
        yield app              # qui girano i test
        db.session.remove()    # pulizia sessione
        db.drop_all()          # elimina le tabelle

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session