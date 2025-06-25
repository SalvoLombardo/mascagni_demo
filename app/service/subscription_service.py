from app.models import db, Subscriber,Subscription,SubscriptionCampaign,PhysicalTicket,Operator

def get_subscribers_by_year(year: int):
    return db.session.query(
        Subscriber.subscriber_first_name,
        Subscriber.subscriber_last_name,
        Operator.operator_username,
        PhysicalTicket.physical_ticket_number
    ).join(Subscription, Subscriber.subscriber_id == Subscription.subscriber_id)\
    .join(SubscriptionCampaign, Subscription.campaign_id == SubscriptionCampaign.campaign_id)\
    .join(PhysicalTicket, Subscription.physical_ticket_id == PhysicalTicket.physical_ticket_id)\
    .join(Operator, Subscription.operator_id == Operator.operator_id)\
    .filter(SubscriptionCampaign.campaign_year == year)\
    .order_by(Subscription.subscription_assigned_at)\
    .all()