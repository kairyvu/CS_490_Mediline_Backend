from flaskr.models import Invoice, Appointment, AppointmentDetail, User
from flaskr.extensions import db
from datetime import datetime, timedelta
from flaskr.struct import PaymentStatus, AppointmentStatus
from flask import jsonify

def get_invoices_by_user(user_id, sort_by='created_at', order='desc'):
    if not hasattr(Invoice, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    
    column = getattr(Invoice, sort_by)
    if order.lower() == 'desc':
        column = column.desc()
    elif order.lower() == 'asc':
        column = column.asc()
    else:
        raise ValueError(f"Invalid order: {order}")
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

def assign_invoice_appoinmtnet(doctor_id, appointment_id, patient_id, requesting_user: User|None=None):
    from flaskr.services import USER_NOT_AUTHORIZED
    appointment = Appointment.query.filter_by(doctor_id = doctor_id, patient_id = patient_id, appointment_id = appointment_id).first()
    if not appointment:
        return jsonify({"error": "Appointment Not found"}), 404

    if ((requesting_user.account_type.name != 'SUPERUSER') 
        and (requesting_user.user_id != doctor_id)):
        return USER_NOT_AUTHORIZED(requesting_user.user_id)
    
    appointment_detail = appointment.appointment_detail
    if appointment_detail.status == AppointmentStatus.COMPLETED:
        return jsonify ({"Message": "Can't Assign Invoices to this Appointment"}), 400
    result = Invoice(
        patient_id = patient_id,
        doctor_id = doctor_id,
        status = PaymentStatus.PENDING,
        created_at = datetime.now(),
        pay_date = datetime.now() + timedelta(weeks=2)
    )

    appointment_detail.status = AppointmentStatus.COMPLETED
    db.session.add(result)
    db.session.commit()
    return jsonify({
        "Message": "Invoice Added Successfully",
        "invoice_id": result.invoice_id,
        "patient_id": result.patient_id,
        "doctor_id": result.doctor_id,
        "status": result.status.name,
        "pay_date": result.pay_date,
        "created_at": result.created_at.strftime("%Y-%m-%d %I:%M %p")
    }), 201

def delete_invoice(doctor_id, invoice_id):
    invoice = Invoice.query.filter_by(invoice_id=invoice_id, doctor_id=doctor_id).first()
    if not invoice:
        return None
    db.session.delete(invoice)
    db.session.commit()

    return {"message": "Invoice deleted successfully"}
