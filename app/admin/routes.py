from flask import Blueprint,request,redirect,url_for,render_template,flash,session
from flask_login import login_user, login_required,logout_user,current_user
from app.extension import db,bcrypt

from app.models import Operator,Subscriber,SubscriptionCampaign,Subscription,PhysicalTicket
from app.forms import AdminSignupForm, AdminLoginForm, NewCampaignEmptyButton,SearchSubscriberForm,ConfirmDelete,DeleteForm,SelectYearFormat,AssignPhysicalTickets

from app.decorators import admin_required

from datetime import datetime

from .utils import assign_ticket

import pandas as pd
from io import BytesIO
from flask import send_file


admin_bp= Blueprint('admin', __name__)


@admin_bp.route('/signin_admin', methods=['GET', 'POST'])
def signin_admin():
    form = AdminSignupForm()

    if form.validate_on_submit():
        #being sure there's not another operator with the same name
        existing_operator=Operator.query.filter_by(operator_username=form.username.data).first()

        if existing_operator:
            flash(f'Non posso creare questo utente perchè esiste già ')
            return redirect(url_for('admin.signin_admin'))
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

            operator = Operator(
                operator_username=form.username.data,
                operator_password=hashed_password,
                operator_first_name=form.first_name.data,
                operator_last_name=form.last_name.data,
                operator_is_admin=True
            )

            db.session.add(operator)
            db.session.commit()

            flash('Ciao Admin, registrazione riuscita, adesso devi fare il Login')
            return redirect(url_for('admin.login_admin'))

    return render_template('signin_admin.html', form=form)


@admin_bp.route('/login_admin', methods=['GET','POST'])
def login_admin():
    form=AdminLoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data

        
        
        operator=Operator.query.filter_by(operator_username=username).first()

        if operator and bcrypt.check_password_hash(operator.operator_password,password) and operator.operator_is_admin==True:
            login_user(operator)
            flash('Admin Login Riuscito')
            return redirect(url_for('admin.main_admin'))
        else:
            flash('Login fallito')
            return redirect(url_for('admin.login_admin'))
        
    return render_template ('login_operator.html', form=form)

@admin_bp.route('/logout_admin',methods=['GET','POST'])
def logout_admin():
    logout_user()
    flash('Logout effettuato')
    return redirect(url_for('main.home')) 

@admin_bp.route('/main_admin',methods=['GET','POST'])
@admin_required
def main_admin():
    return render_template ('main_admin.html')

@admin_bp.route('/main_admin/create_new_campaign',methods=['GET','POST'])
@admin_required
def create_new_campaign():

    form=NewCampaignEmptyButton()

    if form.validate_on_submit():

        current_year=datetime.now().year
        campaign=SubscriptionCampaign.query.filter_by(campaign_year=current_year).first()
        
        if not campaign:
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

            flash('Nuova campagna creata e aggiunti 300 abbonamenti')
            return redirect (url_for('admin.main_admin'))
        else:
            flash('Esiste già una campagna per quest anno')
            return redirect( url_for('admin.main_admin'))

    return render_template('create_new_campaign.html',form=form)






@admin_bp.route('/main_admin/search_who_delete',methods=['GET','POST'])
@admin_required
def search_who_delete():
    form=SearchSubscriberForm()
    delete_form=DeleteForm()
    if form.validate_on_submit():
        subscriber_first_name = form.subscriber_first_name.data.strip()#.capitalize()
        subscriber_last_name=form.subscriber_last_name.data.strip()#.capitalize()

        subscribers = db.session.query(Subscriber).filter(
            Subscriber.subscriber_first_name == subscriber_first_name,
            Subscriber.subscriber_last_name == subscriber_last_name
        ).all()

        if not subscribers:
            flash('Nessun utente trovato')
            return redirect(url_for('admin.search_who_delete'))
        
        return render_template('choose_delete_subscriber.html',subscribers=subscribers,delete_form=delete_form)

    return render_template('search_who_delete.html',form=form)



@admin_bp.route('/main_admin/choose_delete_subscriber',methods=['GET','POST'])
@admin_required
def choose_delete_subscriber():
    return render_template('choose_delete_subscriber.html')


@admin_bp.route('/main_admin/confirm_delete_subscriber',methods=['POST'])
@admin_required
def confirm_delete_subscriber():
    subscriber_id=request.form.get('subscriber_id')#I'm getting this data, was passed trough from in hidden method in choose_delete_subscriber.html

    if not subscriber_id:
        flash('Id utente non valido')
        return redirect(url_for('admin.search_who_delete'))
    
    subscriber=Subscriber.query.get(subscriber_id)

    if not subscriber:
        flash("Utente non trovato.")
        return redirect(url_for('admin.search_who_delete'))

    subscriptions=Subscription.query.filter_by(subscriber_id=subscriber_id).all()
    
    
    for sub in subscriptions:
        ticket = PhysicalTicket.query.get(sub.physical_ticket_id)
        if ticket:
            ticket.physical_ticket_is_available = True

        db.session.delete(sub)
    
    
    db.session.delete(subscriber)

    db.session.commit()

    flash('Utente e tutte le sue iscrizioni cancellate')
    return redirect(url_for('admin.main_admin'))


   
    
@admin_bp.route('/main_admin/delete_campaign',methods=['GET','POST'])
@admin_required
def delete_campaign():
    form=SelectYearFormat()

    available_years=list(range(2020,2040))
    choise=[]
    for y in available_years:
        couple= (y,y)
        choise.append(couple)

    form.year.choices = choise

    if form.validate_on_submit():
        year=form.year.data
        selected_campaign=SubscriptionCampaign.query.filter_by(campaign_year=year).first()

        if selected_campaign:
            subscription=Subscription.query.filter_by(campaign_id=selected_campaign.campaign_id).all()
            physical_ticket=PhysicalTicket.query.filter_by(campaign_id=selected_campaign.campaign_id).all()

            for sub in subscription:
                db.session.delete(sub)
            for ticket in physical_ticket:
                db.session.delete(ticket)
            db.session.delete(selected_campaign)
            db.session.commit()
            flash('Campagna e dati relativi eliminati')
            return redirect(url_for('admin.main_admin'))
        
        flash('Attenzione, anno selezionato inesistente o sbagliato')
        return redirect(url_for('admin.main_admin'))


    
    return render_template('delete_campaign.html',form=form)
    

@admin_bp.route('/main_admin/choose_operator_for_assign',methods=['GET'])
@admin_required
def choose_operator_for_assign():
    
    operator=Operator.query.all()

    return render_template('choose_operator_for_assign.html',operator=operator)


@admin_bp.route('/main_admin/assigned_physical_tickets/<int:operator_id>',methods=['GET','POST'])
@admin_required
def assigned_physical_tickets(operator_id):
    form=AssignPhysicalTickets()

    if form.validate_on_submit():
        
        
        from1=form.from1.data
        to1=form.to1.data
        if from1 and to1:
            first_interval= (from1, to1)
            for n in range(first_interval[0],first_interval[1]+1):
                assign_ticket(n, operator_id) #some refactoring, watch into utils.py        
        elif from1 or to1:
            flash('Attenzione manca un intervallo di date')
            return redirect(url_for('admin.assigned_physical_tickets',operator_id=operator_id))

        from2=form.from2.data
        to2=form.to2.data
        if from2 and to2:
            second_interval= (from2, to2)
            for n in range(second_interval[0],second_interval[1]+1):
                assign_ticket(n, operator_id)
        elif from2 or to2:
            flash('Attenzione manca un intervallo di date')
            return redirect(url_for('admin.assigned_physical_tickets',operator_id=operator_id))

        single_ticket1=form.single_ticket1.data
        single_ticket2=form.single_ticket2.data
        single_ticket3=form.single_ticket3.data
        single_ticket4=form.single_ticket4.data
        single_ticket5=form.single_ticket5.data
        single_ticket6=form.single_ticket6.data
        single_ticket7=form.single_ticket7.data
        single_ticket8=form.single_ticket8.data
        
        for ticket_number in [single_ticket1,single_ticket2,single_ticket3,single_ticket4,single_ticket5,single_ticket6,single_ticket7,single_ticket8]:
            if ticket_number:
                assign_ticket(ticket_number, operator_id)


        db.session.commit()
        
        flash('Abbonamenti assegnati ad operatore')
        return redirect(url_for('admin.main_admin'))


    

    return render_template('assigned_physical_tickets.html',form=form,operator_id=operator_id)

@admin_bp.route('/main_admin/view_assigned_tickets', methods=['GET'])
@admin_required
def view_assigned_tickets():
    from sqlalchemy.orm import joinedload
    

    current_year = datetime.utcnow().year

    tickets = PhysicalTicket.query.join(SubscriptionCampaign).filter(
        SubscriptionCampaign.campaign_year == current_year
    ).with_entities(
        PhysicalTicket.physical_ticket_number,
        PhysicalTicket.assigned_to_operator_id,
        PhysicalTicket.physical_ticket_is_available
    ).order_by(PhysicalTicket.physical_ticket_number).all()

    return render_template("view_assigned_tickets.html", tickets=tickets, year=current_year)


@admin_bp.route('/main_admin/create_telephon_book', methods=['GET'])
@admin_required
def create_telephon_book():

    current_year = datetime.utcnow().year

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

    for first_name, last_name, phone in subscribers:
        string= f'{phone} , {last_name} {first_name}'
        formatted_subscribers.append(string)
    headers =["Numero , Nome Cognome"]
    
    return render_template('create_telephon_book.html',formatted_subscribers=formatted_subscribers, headers =["Numero , Nome Cognome"])


@admin_bp.route('/main_admin/download_excel', methods=['GET'])
@admin_required
def download_excel():
    current_year = datetime.utcnow().year

    subscribers = db.session.query(
        Subscriber.subscriber_first_name,
        Subscriber.subscriber_last_name,
        Subscriber.subscriber_phone_number
    ).join(Subscription, Subscriber.subscriber_id == Subscription.subscriber_id)\
    .join(SubscriptionCampaign, Subscription.campaign_id == SubscriptionCampaign.campaign_id)\
    .filter(SubscriptionCampaign.campaign_year == current_year)\
    .order_by(Subscriber.subscriber_last_name)\
    .all()

    # Formatta come richiesto
    data = [f"{phone} , {last_name} {first_name}" for first_name, last_name, phone in subscribers]

    df = pd.DataFrame(data, columns=["Numero , Nome Cognome"])

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    return send_file(
        output,
        download_name=f"rubrica_{current_year}.xlsx",
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )