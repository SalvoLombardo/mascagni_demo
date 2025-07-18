from app.extension import db
from app.models import SubscriptionCampaign,PhysicalTicket,Subscription,Subscriber
from flask_login import current_user
from flask import flash,url_for,redirect

def new_campaign(current_year):
    try:
        campaign = SubscriptionCampaign(campaign_year=current_year)
        db.session.add(campaign)
        db.session.commit()

        operator_id=current_user.operator_id
        for num in range(1,300):
            ticket = PhysicalTicket(
                physical_ticket_number=num,
                physical_ticket_is_available=True,
                operator_id=operator_id,
                campaign_id=campaign.campaign_id
                )
            db.session.add(ticket)

        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

def total_delete_subscriber(subscriber_id):
    subscriber=Subscriber.query.get(subscriber_id)
    subscriptions=Subscription.query.filter_by(subscriber_id=subscriber_id).all()

    if not subscriber:
        return False
    try: 
        for sub in subscriptions:
            ticket = PhysicalTicket.query.get(sub.physical_ticket_id)
            if ticket:
                ticket.physical_ticket_is_available = True

            db.session.delete(sub)
        
        db.session.delete(subscriber)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

