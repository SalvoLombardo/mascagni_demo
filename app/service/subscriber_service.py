from datetime import datetime
from flask import session,flash
from app.extension import db
from app.models import (Subscriber, Subscription,SubscriptionCampaign,PhysicalTicket, Operator)
from sqlalchemy import exists, and_
from wtforms import ValidationError
def get_available_tickets_for_operator(operator_id):
    return PhysicalTicket.query.filter(
            PhysicalTicket.physical_ticket_is_available == True,
            PhysicalTicket.assigned_to_operator_id == operator_id
        ).all()


def find_duplicates(first_name,last_name):
    return  Subscriber.query.filter_by(
            subscriber_first_name=first_name,
            subscriber_last_name=last_name
        ).all()


def build_pending_subscribers_data(form, operator_id, campaign_id):#passing operator_id and campaign_id, the only variables that doesn't exists in form
    return {
                'first_name': form.first_name.data.strip().capitalize(),#Pass the data direct trough the form "form = AddSubscriberForm()""
                'last_name': form.last_name.data.strip().capitalize(),
                'phone_number': form.phone_number.data.replace(" ",""),
                'note': form.note.data,
                'is_paid': form.is_paid.data,
                'payment_method': form.payment_method.data,
                'subscription_note': form.subscription_note.data,
                'ticket_id': form.ticket_id.data,
                'campaign_id':campaign_id,
                'operator_id':operator_id,
                'subscription_assigned_at':datetime.utcnow()
            }
        

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
        return True
    
    else:
        flash("Abbonato già iscritto per l’anno corrente", "warning")
        return False
    

def get_subscriber_not_paid_by_operator(operator_id: int):
    return Subscription.query.join(PhysicalTicket).filter(
        Subscription.subscription_is_paid == False,
        PhysicalTicket.physical_ticket_is_available == False,
        Subscription.operator_id == operator_id
    ).all()

def find_subscriber_by_operator(subscriber_first_name,subscriber_last_name,operator_id):


    return db.session.query(
            Subscriber.subscriber_id,
            Subscriber.subscriber_first_name,
            Subscriber.subscriber_last_name,
            PhysicalTicket.physical_ticket_number
        )\
        .join(Subscription, Subscriber.subscriber_id == Subscription.subscriber_id)\
        .join(PhysicalTicket, Subscription.physical_ticket_id == PhysicalTicket.physical_ticket_id)\
        .join(SubscriptionCampaign, Subscription.campaign_id == SubscriptionCampaign.campaign_id)\
        .filter(
            Subscriber.subscriber_first_name == subscriber_first_name,
            Subscriber.subscriber_last_name == subscriber_last_name,
            Subscription.operator_id == operator_id,
            SubscriptionCampaign.campaign_year == datetime.now().year
        )\
        .all()

def get_subscriber_and_current_physical_ticket(subscriber_id):
    return db.session.query(
        Subscriber.subscriber_first_name,
        Subscriber.subscriber_last_name,
        Subscriber.subscriber_phone_number,
        Subscriber.subscriber_note,
        PhysicalTicket.physical_ticket_number,
        PhysicalTicket.physical_ticket_id  
    )\
    .join(Subscription, Subscriber.subscriber_id == Subscription.subscriber_id)\
    .join(SubscriptionCampaign, Subscription.campaign_id == SubscriptionCampaign.campaign_id)\
    .join(PhysicalTicket, Subscription.physical_ticket_id == PhysicalTicket.physical_ticket_id)\
    .filter(
        Subscriber.subscriber_id == subscriber_id,
        SubscriptionCampaign.campaign_year == datetime.now().year
    )\
    .first()
