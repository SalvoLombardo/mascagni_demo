from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField,SelectField,IntegerField,ValidationError
from wtforms.validators import DataRequired,NumberRange,Optional

class OperatorSignupForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired()])
    password=PasswordField('Password', validators=[DataRequired()])
    first_name=StringField('Nome', validators=[DataRequired()])
    last_name=StringField('Cognome', validators=[DataRequired()])
    submit=SubmitField('Registrati')

class OperatorLoginForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired()])
    password=PasswordField('Password', validators=[DataRequired()])
    submit=SubmitField('Registrati')
    
class AddSubscriberForm(FlaskForm):

    #Subscriber's data
    first_name = StringField('Nome', validators=[DataRequired()])
    last_name = StringField('Cognome', validators=[DataRequired()])
    phone_number = StringField('Telefono')
    note = TextAreaField('Note')

    #Subscription's data
    is_paid = BooleanField('Pagato')
    payment_method = SelectField('Metodo di pagamento', choices=[
        ('contanti', 'Contanti'),
        ('bonifico', 'Bonifico'),
        ('non_pagato', 'Non Ancora Pagato'),
    ])
    subscription_note = TextAreaField('Note iscrizione')

    #this variable will be completed in his route
    ticket_id = SelectField('Biglietto assegnato', coerce=int, validators=[DataRequired()])

    submit = SubmitField('Aggiungi')



    #with the function down below i make sure that if the operator doesn't select the is_paid flag but
    #leaves the next field (payment method) in 'Cash o  wire transfer', it will be converted automatically 
    #in 'not paid'
    #and if the operator try to save a subscriber who had paid it will raise Valitation Error, which stops the operation
    #and wait the operator that change his choise in another method
    def validate_payment_method(self, field): 
        if self.is_paid.data:
            if field.data == 'non_pagato' or not field.data:
                raise ValidationError(
                    "Hai indicato che è stato pagato, ma non hai scelto un metodo di pagamento valido."
                )
        else:
            
            field.data = 'non_pagato'


    def validate_first_name(form, field):
        if any(char.isdigit() for char in field.data):
            raise ValidationError("Il nome non può contenere numeri.")

    def validate_last_name(form, field):
        if any(char.isdigit() for char in field.data):
            raise ValidationError("Il cognome non può contenere numeri.")
    

class AdminSignupForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired()])
    password=PasswordField('Password', validators=[DataRequired()])
    first_name=StringField('Nome', validators=[DataRequired()])
    last_name=StringField('Cognome', validators=[DataRequired()])
    submit=SubmitField('Registrati')

class AdminLoginForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired()])
    password=PasswordField('Password', validators=[DataRequired()])
    submit=SubmitField('Registrati')




class NewCampaignEmptyButton(FlaskForm):
    pass #I'm using this Flaskform just for the CSRF protection
         #It's not necessary cause you can do it in a simpler way just with csrf_token() in the form(in html file)
         #but i'm doing this just for study porpouse only

class ConfirmExistingOrNotForm(FlaskForm):
    submit = SubmitField('Conferma')

class UpdatePaymentStatusForm(FlaskForm):
    submit = SubmitField('Conferma')

class UpdatingPaymentMethodForm(FlaskForm):
    payment_method = SelectField('Metodo di pagamento', choices=[
        ('contanti', 'Contanti'),
        ('bonifico', 'Bonifico'),
    ])
       
class SearchSubscriberForm(FlaskForm):
    subscriber_first_name= StringField('Nome',validators=[DataRequired()])
    subscriber_last_name = StringField('Cognome', validators=[DataRequired()])
    submit= SubmitField('Cerca')

class ConfirmDelete(FlaskForm):

    submit=SubmitField('Elimina questo Abbonato')

class DeleteForm(FlaskForm):
    pass

class SelectYearFormat(FlaskForm):
    year = SelectField('Seleziona Anno', choices=[], coerce=int, validators=[DataRequired()])
    submit= SubmitField('Elimina questa campagna abbonamenti e i relativi abbonamenti')
    

class AssignPhysicalTickets(FlaskForm):
    from1 = IntegerField('Da:', validators=[
            Optional(),
            NumberRange(min=1, max=300)  
        ])
    to1 = IntegerField('A:', validators=[
            Optional(),
            NumberRange(min=1, max=300)  
        ])
    from2 = IntegerField('Da:', validators=[
            Optional(),
            NumberRange(min=1, max=300)  
        ])
    to2 = IntegerField('A:', validators=[
            Optional(),
            NumberRange(min=1, max=300)  
        ])

    single_ticket1= IntegerField('Abbonamento singolo', validators=[Optional(),NumberRange(min=1, max=300)])
    single_ticket2= IntegerField('Abbonamento singolo', validators=[Optional(),NumberRange(min=1, max=300)])
    single_ticket3= IntegerField('Abbonamento singolo', validators=[Optional(),NumberRange(min=1, max=300)])
    single_ticket4= IntegerField('Abbonamento singolo', validators=[Optional(),NumberRange(min=1, max=300)])
    single_ticket5= IntegerField('Abbonamento singolo', validators=[Optional(),NumberRange(min=1, max=300)])
    single_ticket6= IntegerField('Abbonamento singolo', validators=[Optional(),NumberRange(min=1, max=300)])
    single_ticket7= IntegerField('Abbonamento singolo', validators=[Optional(),NumberRange(min=1, max=300)])
    single_ticket8= IntegerField('Abbonamento singolo', validators=[Optional(),NumberRange(min=1, max=300)])

    submit = SubmitField('Invio')

    def is_any_field_filled(self):#creating a function to check if almost one field is not empty
        return any([
            self.from1.data, self.to1.data,
            self.from2.data, self.to2.data,
            self.single_ticket1.data, self.single_ticket2.data,
            self.single_ticket3.data, self.single_ticket4.data,
            self.single_ticket5.data, self.single_ticket6.data,
            self.single_ticket7.data, self.single_ticket8.data
        ])
    
class SubscriberInfoForm(FlaskForm):
    subscriber_first_name= StringField('Nome',validators=[DataRequired()])
    subscriber_last_name= StringField('Cognome',validators=[DataRequired()])
    subscriber_phone_number= StringField('Telefono')
    subscriber_note= TextAreaField('Note')
    ticket_id=StringField("Abbonamento attuale", render_kw={"readonly": True})
    new_physical_ticket_number= SelectField('Seleziona numero di abbonamento nuovo', coerce=int, validators=[DataRequired(message="Seleziona un ticket")])

    submit= SubmitField('Aggiorna abbonato')
    