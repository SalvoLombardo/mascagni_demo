from app.models import Subscriber, db ,Subscription,PhysicalTicket
from flask_login import current_user
from datetime import datetime

def save_new_subscriber_and_subscription(data, is_new_subscriber):
    if is_new_subscriber:
        #I use the boolean variable is_new_subscriber to create a diffrent way to add an existing subscriber
        #with a new subscription
        #and an already subscriber with a new subscriptio

        new_subscriber=Subscriber(
            subscriber_first_name=data['first_name'],
            subscriber_last_name=data['last_name'],
            subscriber_phone_number=data['phone_number'],
            subscriber_note=data['note']
        )
        db.session.add(new_subscriber)
        db.session.commit()
        subscriber_id= new_subscriber.subscriber_id # An important aspect is that a new subscriber got a new id and
                                                    # this variable is passed on new subscription section(down below)

    else:
        subscriber_id= data['existing_subscriber_id']# but the id in this case is different beacuse it already exist
        
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


    


