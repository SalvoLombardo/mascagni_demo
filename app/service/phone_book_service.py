from app.extension import db
from app.models import SubscriptionCampaign,PhysicalTicket,Subscription,Subscriber
from flask_login import current_user
import pandas as pd
from io import BytesIO



def get_sub_for_telephone_book(current_year):
    subscribers = db.session.query(
        Subscriber.subscriber_first_name,
        Subscriber.subscriber_last_name,
        Subscriber.subscriber_phone_number
    ).join(Subscription, Subscriber.subscriber_id == Subscription.subscriber_id)\
    .join(SubscriptionCampaign, Subscription.campaign_id == SubscriptionCampaign.campaign_id)\
    .filter(SubscriptionCampaign.campaign_year == current_year)\
    .order_by(Subscriber.subscriber_last_name)\
    .all()
    
    formatted_subscribers=[]
    subscriber_without_phone=[]

    for first_name, last_name, phone in subscribers:
        string= f'{phone} , {last_name} {first_name}'
        if phone:
            formatted_subscribers.append(string)
        else:
            subscriber_without_phone.append(string)
    return  formatted_subscribers , subscriber_without_phone



#Block for get excel output
def get_phonebook_subscribers(current_year):
    return db.session.query(
        Subscriber.subscriber_first_name,
        Subscriber.subscriber_last_name,
        Subscriber.subscriber_phone_number
    ).join(Subscription, Subscriber.subscriber_id == Subscription.subscriber_id)\
     .join(SubscriptionCampaign, Subscription.campaign_id == SubscriptionCampaign.campaign_id)\
     .filter(SubscriptionCampaign.campaign_year == current_year)\
     .order_by(Subscriber.subscriber_last_name)\
     .all()

def format_phonebook_rows(subscribers):
    return [f"{phone } , {last} {first}" for first, last, phone in subscribers]

def generate_phonebook_excel(formatted_rows):
    df = pd.DataFrame(formatted_rows, columns=["Numero , Nome Cognome"])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output
