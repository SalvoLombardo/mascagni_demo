from app.models import PhysicalTicket
from flask import current_app, flash

def assign_ticket(ticket_number,operator_id):
    physical=PhysicalTicket.query.filter_by(physical_ticket_number=ticket_number).first()

    if physical and physical.physical_ticket_is_available==True and physical.assigned_to_operator_id==None:
        physical.assigned_to_operator_id=operator_id

    else:
        flash(f'Attenzione il biglietto numero {ticket_number} è stato venduto o già assegnato ad un altro operatore')
        