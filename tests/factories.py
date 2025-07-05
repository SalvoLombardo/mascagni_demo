from datetime import datetime
from app.models import Operator, SubscriptionCampaign, PhysicalTicket, Subscriber,Subscription
from app.extension import db

def make_operator(
    username="alice",
    password="hashed",
    first_name="Alice",
    last_name="Rossi",
    is_admin=False,
    ):
    
    op = Operator(
        operator_username=username,
        operator_password=password,
        operator_first_name=first_name,
        operator_last_name=last_name,
        operator_is_admin=is_admin,
    )
    db.session.add(op)
    db.session.flush()          # ottieni subito op.operator_id
    return op

def make_campaign(year=None):
    camp = SubscriptionCampaign(campaign_year=year or datetime.now().year)
    db.session.add(camp)
    db.session.flush()
    return camp

def make_ticket(number, operator_id, campaign_id, available=True):
    t = PhysicalTicket(
        physical_ticket_number=number,
        physical_ticket_is_available=available,
        assigned_to_operator_id=operator_id,
        operator_id=operator_id,
        campaign_id=campaign_id,
    )
    db.session.add(t)
    db.session.flush()
    return t

def make_subscriber(first_name, last_name, phone_number="0000", note=""):
    sub = Subscriber(
        subscriber_first_name=first_name,
        subscriber_last_name=last_name,
        subscriber_phone_number=phone_number,
        subscriber_note=note,
    )
    db.session.add(sub)
    db.session.flush()
    return sub
    


def make_subscription(subscription_is_paid,subscription_payment_method,subscription_note,physical_ticket_id ,subscriber_id,campaign_id,operator_id):
    
    subscription=Subscription(
        subscription_is_paid=subscription_is_paid,
        subscription_payment_method=subscription_payment_method,
        subscription_note=subscription_note,
        physical_ticket_id =physical_ticket_id,
        subscriber_id=subscriber_id,
        campaign_id=campaign_id,
        operator_id=operator_id
    )
    db.session.add(subscription)
    db.session.commit()
    return subscription