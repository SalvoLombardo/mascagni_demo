from datetime import datetime
from flask import session
from app.extension import db
from app.models import (Subscriber, Subscription,SubscriptionCampaign,PhysicalTicket, Operator)


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
                'phone_number': form.phone_number.data.strip(),
                'note': form.note.data,
                'is_paid': form.is_paid.data,
                'payment_method': form.payment_method.data,
                'subscription_note': form.subscription_note.data,
                'ticket_id': form.ticket_id.data,
                'campaign_id':campaign_id,
                'operator_id':operator_id,
                'subscription_assigned_at':datetime.utcnow()
            }
        