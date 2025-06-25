from flask import Blueprint,request,redirect,url_for,render_template,flash,session,Response
from flask_login import login_user, login_required,logout_user,current_user
from flask_wtf.csrf import generate_csrf
from app.extension import db,bcrypt
from datetime import datetime

#MODELS
from app.models import Operator,Subscriber,SubscriptionCampaign,Subscription,PhysicalTicket

#FLASK FORM
from app.forms import OperatorSignupForm, OperatorLoginForm, AddSubscriberForm ,ConfirmExistingOrNotForm ,UpdatePaymentStatusForm ,UpdatingPaymentMethodForm ,SearchSubscriberForm

#REFACTORY SECTION - SERVICE IMPORT
from app.service import subscriber_service as subscriber_service
from app.service import subscription_service as subscription_service
from app.exporter import subscriber_exporter as exp_service

from .utils import save_new_subscriber_and_subscription

auth_bp= Blueprint('auth', __name__)

#####################################################################
#################     SIGN IN LOGING LOGOUT    ######################
#################          SECTION             ######################
@auth_bp.route('/signin_operator', methods=['GET', 'POST'])
def signin_operator():
    form = OperatorSignupForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        operator = Operator(
            operator_username=form.username.data,
            operator_password=hashed_password,
            operator_first_name=form.first_name.data,
            operator_last_name=form.last_name.data
        )

        db.session.add(operator)
        db.session.commit()

        flash('Registrazione riuscita, adesso devi fare il Login')
        return redirect(url_for('auth.login_operator'))

    return render_template('signin_operator.html', form=form)

@auth_bp.route('/login_operator', methods=['GET','POST'])
def login_operator():
    form=OperatorLoginForm()
    if form.validate_on_submit():
        username=form.username.data.strip()
        password=form.password.data

        
        
        operator=Operator.query.filter_by(operator_username=username).first()

        if operator and bcrypt.check_password_hash(operator.operator_password,password):
            login_user(operator)
            flash('login Riuscito')
            return redirect(url_for('auth.main_operator'))
        else:
            flash('Login fallito')
            return redirect(url_for('auth.login_operator'))
        
    return render_template ('login_operator.html', form=form)

@auth_bp.route('/logout_operator',methods=['GET','POST'])
def logout_operator():
    logout_user()
    flash('Logout effettuato')
    return redirect(url_for('main.home')) 

@auth_bp.route('/main_operator', methods=['GET', 'POST'])
@login_required
def main_operator():
    return render_template('main_operator.html', operator=current_user)





#####################################################################
#################ADD SUBSCRIBER OR SUBSCRIPTION######################
#################          SECTION             ######################
@auth_bp.route('/main_operator/add_subscriber', methods=['GET', 'POST'])
@login_required
def add_subscriber():
    form = AddSubscriberForm()

    available_tickets_for_operator= subscriber_service.get_available_tickets_for_operator(current_user.operator_id)
    form.ticket_id.choices = [
        (t.physical_ticket_id, f"Biglietto n° {t.physical_ticket_number}")
        for t in available_tickets_for_operator
    ]
    
    if form.validate_on_submit():
        first_name = form.first_name.data.strip().capitalize()
        last_name = form.last_name.data.strip().capitalize()

        duplicates=subscriber_service.find_duplicates(first_name,last_name)
        #Searching with query on subscriber if there is another subscriber with the same first name and last name
        #if existing has some values means that there are some duplicates or some homonym
        #Decided to save the data on a session to pass it though the process
        
        campaign = SubscriptionCampaign.query.filter_by(campaign_year=datetime.now().year).first()
        
        data=subscriber_service.build_pending_subscribers_data(form,operator_id=current_user.operator_id,campaign_id=campaign.campaign_id)
        session['pending_subscriber'] = data
                

        if duplicates:
            return render_template('confirm_existing_subscriber.html', existing=duplicates, form=ConfirmExistingOrNotForm())#Passing this for direct here(used just for CSRF protection)

        else:
            return redirect(url_for('auth.add_subscriber_confirm'))
        
    return render_template('add_subscriber.html', form=form)

@auth_bp.route('/main_operator/add_subscriber/confirm', methods=['GET', 'POST'])
@login_required
def add_subscriber_confirm():
    
    data=session.pop('pending_subscriber',None)
    is_new_subscriber=True

    if data:
        
        succes=save_new_subscriber_and_subscription(data,is_new_subscriber)
        if succes:
            flash('Nuovo abbonato aggiunto con successo')
        else:
            flash('Attenzione questo abbonato risulta avere una inscrizione alla stagione corrente ')
            return redirect (url_for('auth.main_operator'))
    
    else:
        flash('Errore: Qualcosa è andato storto, nessun dato presente, riprova')

    return redirect(url_for('auth.success_page'))

@auth_bp.route('/main_operator/add_subscriber/confirm_existing_subscriber/<int:subscriber_id>', methods=['POST'])
@login_required 
def confirm_existing_subscriber(subscriber_id):
    data = session.pop('pending_subscriber', None)
    is_new_subscriber=False

    if not data:
        flash("Dati di iscrizione non trovati. Riprova.", "error")
        return redirect(url_for('auth.add_subscriber'))
    
    data['existing_subscriber_id']=subscriber_id
    success = save_new_subscriber_and_subscription(data, is_new_subscriber)
    if success:
        flash('Vecchio abbonato inserito nella nuova stagione concertistica', 'success')
        return redirect(url_for('auth.success_page'))
    else:
        flash("Abbonato già iscritto per l’anno corrente", "warning")
        return redirect(url_for('auth.main_operator'))

    flash('Vecchio abbonato inserito nella nuova stagione concertistica', 'success')
    return render_template('success_page.html')

@auth_bp.route('/main_operator/add_subscriber/confirm/success_page')
@login_required
def success_page():
    return render_template('success_page.html')
   




#####################################################################
########################    PAYMENT SITUATION      ##################
#################              SECTION             ##################
@auth_bp.route('/main_operator/who_needs_to_pay', methods=['GET', 'POST'])
@login_required
def who_needs_to_pay():

    

    subscriptions = Subscription.query\
    .join(PhysicalTicket)\
    .join(Subscriber)\
    .filter(
        Subscription.subscription_is_paid == False,
        PhysicalTicket.physical_ticket_is_available == False
    ).all()

    
    return render_template('who_needs_to_pay.html', subscriptions=subscriptions)

@auth_bp.route('/main_operator/updating_paying_situation', methods=['GET', 'POST'])
@login_required
def updating_paying_situation():
    form = UpdatingPaymentMethodForm()
    if form.validate_on_submit():
        subscription_id = request.form.get('subscription_id')
        subscription = Subscription.query.get_or_404(subscription_id)
        subscription.subscription_is_paid = True
        subscription.subscription_payment_method = form.payment_method.data
        db.session.commit()
        return redirect(url_for('auth.main_operator'))

    subscriptions = Subscription.query.join(PhysicalTicket).filter(
        Subscription.subscription_is_paid == False,
        PhysicalTicket.physical_ticket_is_available == False,
        Subscription.operator_id == current_user.operator_id
    ).all()

    return render_template('updating_paying_situation.html', subscriptions=subscriptions, form=form)





#####################################################################
########################VIEW SUBSCRIBER BY YEAR######################
#################              SECTION             ##################
@auth_bp.route('/main_operator/select_year', methods=['GET','POST'])
@login_required
def select_year():
    if request.method=='GET':
        return render_template('select_year.html')
    
    if request.method=='POST':
        selected_year = request.form.get('year', type=int)
        return redirect(url_for('auth.view_all_subscribers_by_year', selected_year=selected_year))
    
@auth_bp.route('/main_operator/view_all_subscribers_by_year/<int:selected_year>', methods=['GET','POST'])
@login_required
def view_all_subscribers_by_year(selected_year):

    subscribers = subscription_service.get_subscribers_by_year(selected_year)

    if request.method=='POST':
        output= exp_service.export_subscribers_xlsx(subscribers, selected_year)
        return Response(
            output,
            mimetype=(
                "application/vnd."
                "openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition":
                f"attachment; filename=subscribers_{selected_year}.xlsx"
            },
        )

    headers = ["Nome", "Cognome", "Operatore", "N. abbonamento"]#for the table
    return render_template('view_all_subscribers_by_year.html', subscribers=subscribers, year=selected_year, headers=headers)












@auth_bp.route('/main_operator/search_subscriber_by_operator', methods=['GET','POST'])
@login_required
def search_subscriber_by_operator():
    form=SearchSubscriberForm()

    if form.validate_on_submit():
        subscriber_first_name = form.subscriber_first_name.data.strip().capitalize()
        subscriber_last_name=form.subscriber_last_name.data.strip().capitalize()

        result = db.session.query(
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
            Subscription.operator_id == current_user.operator_id,
            SubscriptionCampaign.campaign_year == datetime.now().year
        )\
        .all()

        return render_template('search_results.html',result=result)


    return render_template('search_subscriber_by_operator.html', form=form)



