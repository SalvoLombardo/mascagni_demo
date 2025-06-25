from app.extension import db

from flask_login import UserMixin

from datetime import datetime

class Subscriber(db.Model):
    __tablename__='subscribers'
    subscriber_id=db.Column(db.Integer, primary_key=True)
    subscriber_first_name=db.Column(db.String(100), nullable=False)
    subscriber_last_name=db.Column(db.String(100), nullable=False)
    subscriber_phone_number=db.Column(db.String(20),index=True)
    subscriber_note=db.Column(db.Text)

    #DB relationship, a way to comunicate in a better way in some query to get something like (subscription.subscriber_first_name) like an extension of a class
    subscriptions = db.relationship('Subscription', backref='subscriber', lazy=True)
    
    def get_id(self):
        return str(self.subscriber_id)
    
    def __repr__(self):
        return f"ABBONATO:| {self.subscriber_first_name} {self.subscriber_last_name} |  NUMERO DI TELEFONO:| {self.subscriber_phone_number} | NOTE :| {self.subscriber_note}| "

class Operator(db.Model, UserMixin):
    __tablename__='operators'
    operator_id=db.Column(db.Integer, primary_key=True)
    operator_username=db.Column(db.String(100),unique=True, nullable=False)
    operator_password=db.Column(db.String(100), nullable=False)
    operator_first_name=db.Column(db.String(100), nullable=False)
    operator_last_name=db.Column(db.String(100), nullable=False)
    operator_is_admin=db.Column(db.Boolean,nullable=False,default=False)

    
    
    def get_id(self):
        return str(self.operator_id)

class SubscriptionCampaign(db.Model):
    __tablename__ = 'subscription_campaigns'
    
    campaign_id = db.Column(db.Integer, primary_key=True)
    campaign_year = db.Column(db.Integer, nullable=False, index=True, unique=True)

    def get_id(self):
        return str(self.campaign_id)
    
class Subscription(db.Model):
    __tablename__='subscriptions'
    subscription_id=db.Column(db.Integer, primary_key=True)
    subscription_is_paid=db.Column(db.Boolean,nullable=False, default=False)
    subscription_payment_method=db.Column(db.String(100))
    subscription_assigned_at=db.Column(db.DateTime, default=datetime.utcnow)
    subscription_note=db.Column(db.Text)

    #FK of PhysicalTicket
    physical_ticket_id = db.Column(db.Integer, db.ForeignKey('physical_tickets.physical_ticket_id'), nullable=False)
    #FK of SubscriberModel
    subscriber_id=db.Column(db.Integer,db.ForeignKey('subscribers.subscriber_id'),nullable=False,index=True)
    #FK of Subscription_campaignModel
    campaign_id=db.Column(db.Integer, db.ForeignKey('subscription_campaigns.campaign_id'),nullable=False,index=True)
    #FK oof OperatorModel
    operator_id=db.Column(db.Integer, db.ForeignKey('operators.operator_id'),nullable=False)

    
    
    
    
    

    def get_id(self):
        return str(self.subscription_id)
    
    def __repr__(self):
        return f"Subcription:| {self.subscription_id}  "

class PhysicalTicket(db.Model):
    __tablename__='physical_tickets'
    physical_ticket_id=db.Column(db.Integer, primary_key=True)
    physical_ticket_number=db.Column(db.Integer, nullable=False,index=True)
    physical_ticket_is_available=db.Column(db.Boolean, default=True)
    assigned_to_operator_id = db.Column(db.Integer, db.ForeignKey('operators.operator_id'), nullable=True)

    #FK of OperatorModel
    operator_id=db.Column(db.Integer, db.ForeignKey('operators.operator_id'),nullable=False)
    #FK of Subscription_campaignModel
    campaign_id=db.Column(db.Integer, db.ForeignKey('subscription_campaigns.campaign_id'),nullable=False)


    #DB relationship, a way to comunicate in a better way in some query to get something like (subscription.subscriber_first_name) like an extension of a class
    subscription = db.relationship('Subscription', backref='physical_ticket', uselist=False)
    campaign = db.relationship('SubscriptionCampaign', backref='physical_tickets')

    def get_id(self):
        return str(self.physical_ticket_id)


