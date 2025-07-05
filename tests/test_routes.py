# tests/test_routes.py
from flask import url_for
from app.models import Operator, PhysicalTicket
from app.extension import bcrypt, db

# --------------------------------------------------------
# 1) LOGIN OPERATOR
# --------------------------------------------------------

def test_login_operator_get(client):
    """La GET deve restituire la pagina di login."""
    resp= client.get("/login_operator")
    assert resp.status_code==200
    assert b"username" in resp.data.lower()   # nel form c'è il campo username


def test_login_operator_post_success(client, app):
    """POST con credenziali corrette deve fare redirect a /main_operator."""
    
    with app.app_context():
        pwd_hash= bcrypt.generate_password_hash("secret").decode()
        op= Operator(
            operator_username="testuser",
            operator_password=pwd_hash,
            operator_first_name="Test",
            operator_last_name="User",
        )
        db.session.add(op)
        db.session.commit()

    # POST
    resp = client.post(
        "/login_operator",
        data={"username": "testuser", "password": "secret"},
        follow_redirects=False,
    )

    
    assert resp.status_code == 302
    assert "/main_operator" in resp.headers["Location"]



def test_add_subscriber_requires_login(client):
    """Senza login, /add_subscriber deve reindirizzare al login."""
    resp= client.get("/main_operator/add_subscriber")
    
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def login(client, username, password):
    """Helper per effettuare il login nel test‐client."""
    return client.post(
        "/login_operator",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_add_subscriber_get_ok(client, app):
    """Con operatore loggato e almeno 1 biglietto disponibile la pagina deve aprirsi."""
    with app.app_context():
        
        pwd_hash= bcrypt.generate_password_hash("secret").decode()
        op = Operator(
            operator_username="op1",
            operator_password=pwd_hash,
            operator_first_name="Mario",
            operator_last_name="Rossi",
        )
        db.session.add(op)
        db.session.flush()   

        
        ticket= PhysicalTicket(
            physical_ticket_number="001",
            physical_ticket_is_available=True,
            assigned_to_operator_id=op.operator_id,
            operator_id=op.operator_id,
            campaign_id=1,          
        )
        db.session.add(ticket)
        db.session.commit()

    
    login(client, "op1", "secret")

    # GET 
    resp = client.get("/main_operator/add_subscriber")
    assert resp.status_code == 200
    assert b"Biglietto" in resp.data      