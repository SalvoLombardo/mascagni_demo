"""
from app.models import Subscriber, db ,Subscription,PhysicalTicket,SubscriptionCampaign
from flask_login import current_user
from datetime import datetime
from sqlalchemy import exists, and_
from flask import flash

def get_subscription_this_year(subscriber_id :int): #This gives me a boolean result to just know if it's true or not
    current_year = datetime.now().year
    return db.session.query(
        exists().where(
            and_(Subscription.subscriber_id == subscriber_id,
                 Subscription.campaign_id == SubscriptionCampaign.campaign_id,
                 SubscriptionCampaign.campaign_year == current_year)
        )
    ).scalar() #Using scalar for boolean result

def save_new_subscriber_and_subscription(data, is_new_subscriber):
    
    if is_new_subscriber:
        #I use the boolean variable is_new_subscriber to create a diffrent way to add an existing subscriber
        #with a new subscription
        #and an already subscriber with a new subscription
        new_subscriber=Subscriber(
            subscriber_first_name=data['first_name'],
            subscriber_last_name=data['last_name'],
            subscriber_phone_number=data['phone_number'],
            subscriber_note=data['note']
        )
        db.session.add(new_subscriber)
        db.session.flush() #Using 'flush' to be sure that there will not be a problem with the second commit(in new subscription section)

        subscriber_id= new_subscriber.subscriber_id # An important aspect is that a new subscriber got a new id and
                                                    # this variable is passed on new subscription section(down below)

    else:
        subscriber_id= data['existing_subscriber_id']# but the id in this case is different beacuse it already exist





    is_subscribed_this_year=get_subscription_this_year(subscriber_id)

    if not is_subscribed_this_year:
        new_subscription= Subscription( 
            subscription_is_paid=data.get('is_paid', False),
            subscription_payment_method=data.get('payment_method', None),
            subscription_note=data.get('subscription_note', ''),
            physical_ticket_id=data['ticket_id'],
            subscriber_id=subscriber_id, # so this variable depends on result of the previous situation 
            campaign_id=data['campaign_id'],
            operator_id=data['operator_id'],
            subscription_assigned_at=data['subscription_assigned_at']
        )
        db.session.add(new_subscription)

        
        physical_ticket = PhysicalTicket.query.get(data['ticket_id'])
        
        physical_ticket.physical_ticket_is_available = False

        db.session.commit()
    
    else:
        flash("Abbonato già iscritto per l’anno corrente", "warning")
        return False


    

"""
