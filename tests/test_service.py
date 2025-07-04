from datetime import datetime, UTC
from app.extension import db
from app.service.subscriber_service import (
    get_available_tickets_for_operator,
    find_duplicates,
    save_new_subscriber_and_subscription,
)
from app.models import Subscriber, Subscription, PhysicalTicket
from tests.factories import make_operator,make_campaign,make_ticket,make_subscriber


# ──────────────────────────────────────────────────────────
def test_get_available_tickets_only_returns_available_for_given_operator(db_session):
    op1 = make_operator(username="operatore1", first_name="Aldo", last_name="Baglio")
    op2 = make_operator(username="operatore2", first_name="Giovanni", last_name="Giacomo")
    camp = make_campaign()

    make_ticket(1, operator_id=op1.operator_id, campaign_id=camp.campaign_id, available=True)
    make_ticket(2, operator_id=op1.operator_id, campaign_id=camp.campaign_id, available=True)
    make_ticket(3, operator_id=op1.operator_id, campaign_id=camp.campaign_id, available=False)
    make_ticket(4, operator_id=op2.operator_id, campaign_id=camp.campaign_id, available=True)

    db_session.commit()

    tickets = get_available_tickets_for_operator(op1.operator_id)
    numbers = [t.physical_ticket_number for t in tickets]

    assert len(tickets) == 2
    assert set(numbers) == {1, 2}

# ──────────────────────────────────────────────────────────
def test_find_duplicates(db_session):
    make_subscriber("mario", "rossi", "0000")
    make_subscriber("mario", "rossi", "1111", "from ireland")
    make_subscriber("mario", "rossi", "2222", "from italy")
    make_subscriber("paolo", "rossi", "3333")

    db_session.commit()

    result = find_duplicates("mario", "rossi")
    names = {(r.subscriber_first_name, r.subscriber_last_name) for r in result}

    assert len(result) == 3
    assert names == {("mario", "rossi")}

# ──────────────────────────────────────────────────────────
def test_save_new_subscriber_and_subscription(db_session):
    op = make_operator(username="operatore")
    camp = make_campaign()
    ticket = make_ticket(1, operator_id=op.operator_id, campaign_id=camp.campaign_id)

    data = {
        "first_name": "Paolo",
        "last_name": "Rossi",
        "phone_number": "0000",
        "note": "nothing",
        "is_paid": False,
        "payment_method": "contanti",
        "subscription_note": "",
        "ticket_id": ticket.physical_ticket_id,
        "campaign_id": camp.campaign_id,
        "operator_id": op.operator_id,
        "subscription_assigned_at": datetime.now(UTC),
    }

    result = save_new_subscriber_and_subscription(data, is_new_subscriber=True)
    assert result is True

    # verifica effetti sul DB
    assert Subscriber.query.count() == 1
    assert Subscription.query.count() == 1
    assert db.session.get(PhysicalTicket, ticket.physical_ticket_id).physical_ticket_is_available is False



def test_save_new_subscriber_duplicate_same_year(db_session):
    op = make_operator()
    camp = make_campaign()
    ticket1 = make_ticket(1, op.operator_id, camp.campaign_id)
    ticket2 = make_ticket(2, op.operator_id, camp.campaign_id)

    # first insertion
    data = {
        "first_name": "Paolo",
        "last_name": "Rossi",
        "phone_number": "0000",
        "note": "nothing",
        "is_paid": False,
        "payment_method": "contanti",
        "subscription_note": "",
        "ticket_id": ticket1.physical_ticket_id,
        "campaign_id": camp.campaign_id,
        "operator_id": op.operator_id,
        "subscription_assigned_at": datetime.now(UTC),
    }
    assert save_new_subscriber_and_subscription(data, True) is True

    #second insertion
    data2 = {
        "first_name": "Paolo",
        "last_name": "Rossi",
        "phone_number": "0000",
        "note": "nothing",
        "is_paid": True,
        "payment_method": "contanti",
        "subscription_note": "",
        "ticket_id": ticket2.physical_ticket_id,
        "campaign_id": camp.campaign_id,
        "operator_id": op.operator_id,
        "subscription_assigned_at": datetime.now(UTC),
        "existing_subscriber_id": 1
    }
    
    
    assert save_new_subscriber_and_subscription(data2, False) is False
    assert Subscription.query.count() == 1