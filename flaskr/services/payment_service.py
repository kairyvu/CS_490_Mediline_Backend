from flaskr.models import Invoice, Appointment
from flaskr.extensions import db
from datetime import datetime, timedelta
from flaskr.struct import PaymentStatus

def get_invoices_by_user(user_id, sort_by='created_at', order='desc'):
    if not hasattr(Invoice, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    
    column = getattr(Invoice, sort_by)
    if order == 'desc':
        column = column.desc()
    invoices = Invoice.query.filter_by(patient_id=user_id).order_by(column).all()
    return [invoice.to_dict() for invoice in invoices]

def update_invoice_status(patient_id, invoice_id, new_status):
    invoice = Invoice.query.filter_by(invoice_id = invoice_id, patient_id = patient_id).first()
    if not invoice:
        return None
    if invoice.status.name != "PENDING":
        return {"error": "No Pending Invoice Found to update"}, 400
    
    invoice.status = PaymentStatus[new_status]
    db.session.commit()
    return invoice.to_dict()

def assign_invoice_appoinmtnet(doctor_id, appointment_id, patient_id):
    appointment = Appointment.query.filter_by(doctor_id = doctor_id, patient_id = patient_id, appointment_id = appointment_id).first()
    if not appointment:
        return None
    
    result = Invoice(
        patient_id = patient_id,
        doctor_id = doctor_id,
        status = PaymentStatus.PENDING,
        created_at = datetime.now(),
        pay_date = datetime.now() + timedelta(weeks=2)
    )

    db.session.add(result)
    db.session.commit()
    return{
        "invoice_id": result.invoice_id,
        "patient_id": result.patient_id,
        "doctor_id": result.doctor_id,
        "status": result.status.name,
        "pay_date": result.pay_date,
        "created_at": result.created_at.strftime("%Y-%m-%d %I:%M %p")
    }
