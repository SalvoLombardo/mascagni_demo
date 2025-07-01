from app.extension import db
from app.models import SubscriptionCampaign,PhysicalTicket
from flask_login import current_user

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
