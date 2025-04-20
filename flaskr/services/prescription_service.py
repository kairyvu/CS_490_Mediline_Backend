from flaskr.models import Prescription, Doctor, Patient
from flaskr.extensions import db
from sqlalchemy import func, case
from flaskr.struct import PrescriptionStatus


def get_prescriptions(user_id, sort_by='created_at', order='asc'):
    is_patient = Patient.query.filter_by(user_id=user_id).first() is not None
    is_doctor = Doctor.query.filter_by(user_id=user_id).first() is not None

    if not (is_patient or is_doctor):
        raise ValueError("User not found as either patient or doctor")

    query = Prescription.query
    if is_patient:
        query = query.filter(Prescription.patient_id == user_id)
    elif is_doctor:
        query = query.filter(Prescription.doctor_id == user_id)

    if not hasattr(Prescription, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    column = getattr(Prescription, sort_by)
    if order == 'desc':
        column = column.desc()
    query = query.order_by(column)
    prescriptions = query.all()
    return [prescription.to_dict() for prescription in prescriptions]

def get_medications_by_prescription(prescription_id):
    prescription = Prescription.query.get(prescription_id)
    if not prescription:
        raise ValueError("Prescription not found")
    medications_list = []

    for pres_med in prescription.prescription_medications:
        med_details = pres_med.medication.to_dict()
        med_details.update({
            "prescription_medication_id": pres_med.prescription_medication_id,
            "dosage": pres_med.dosage,
            "medical_instructions": pres_med.medical_instructions
        })
        medications_list.append(med_details)
    return medications_list

def get_prescription_count_by_pharmacy(pharmacy_id):
    rows = (
        db.session.query(
            Prescription.status,
            func.count(Prescription.prescription_id)
        ).filter(Prescription.pharmacy_id == pharmacy_id)
        .group_by(Prescription.status)
        .all()
    )
    counts = { status: count for status, count in rows }
    
    return {
        'collected_prescription': counts.get(PrescriptionStatus.PAID, 0),
        'processing_prescription': counts.get(PrescriptionStatus.UNPAID, 0)
    }