from flaskr.models import User, Prescription, Doctor, Patient, Pharmacy, Inventory, PrescriptionMedication
from flaskr.extensions import db
from sqlalchemy import func
from flaskr.struct import PrescriptionStatus

def get_prescriptions(user_id, sort_by='created_at', order='asc'):
    is_patient = Patient.query.filter_by(user_id=user_id).first() is not None
    is_doctor = Doctor.query.filter_by(user_id=user_id).first() is not None
    is_pharmacy = Pharmacy.query.filter_by(user_id=user_id).first() is not None

    if not (is_patient or is_doctor or is_pharmacy):
        raise ValueError("User not found as either patient, doctor or pharmacy")

    query = Prescription.query
    if is_patient:
        query = query.filter(Prescription.patient_id == user_id)
    elif is_doctor:
        query = query.filter(Prescription.doctor_id == user_id)
    elif is_pharmacy:
        query = query.filter(Prescription.pharmacy_id == user_id)

    if not hasattr(Prescription, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    column = getattr(Prescription, sort_by)
    if order.lower() == 'desc':
        column = column.desc()
    elif order.lower() == 'asc':
        column = column.asc()
    else:
        raise ValueError(f"Invalid order: {order}")
    query = query.order_by(column)
    prescriptions = query.all()
    return [prescription.to_dict() for prescription in prescriptions]

def get_medications_by_prescription(prescription_id, requesting_user: User|None=None):
    from flaskr.services import UnauthorizedError
    prescription = Prescription.query.get(prescription_id)
    if not prescription:
        raise ValueError("Prescription not found")
    medications_list = []
    if requesting_user:
        match requesting_user.account_type.name:
            case 'SuperUser':
                pass
            case 'Patient' \
                if requesting_user.user_id == prescription.patient_id:
                pass
            case 'Doctor' \
                if requesting_user.user_id == prescription.doctor_id:
                pass
            case 'Pharmacy' \
                if requesting_user.user_id == prescription.pharmacy_id:
                pass
            case _:
                return UnauthorizedError
    else:
        return UnauthorizedError

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

def get_pharmacy_medications_inventory(pharmacy_id):
    inventory = Inventory.query.filter_by(pharmacy_id=pharmacy_id).all()
    if not inventory:
        raise ValueError("No medications found in the pharmacy inventory")
    medications_list = []
    for item in inventory:
        medications_list.append(item.to_dict())
    return medications_list

def get_medications_history_by_patient(patient_id):
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()
    if not prescriptions:
        raise ValueError("No prescriptions found for the patient")
    medications_history = []
    for prescription in prescriptions:
        medications = get_medications_by_prescription(prescription.prescription_id)
        medications_history.append(medications)
    return medications_history

def update_medication_inventory(prescription_id, status: PrescriptionStatus):
    pharmacy_id = Prescription.query.get(prescription_id).pharmacy_id
    if not pharmacy_id:
        raise ValueError("Pharmacy not found for the prescription")
    prescription_medications = PrescriptionMedication.query.filter_by(prescription_id=prescription_id).all()
    if not prescription_medications:
        raise ValueError("No medications found for the prescription")

    for medication in prescription_medications:
        inventory_item = Inventory.query.filter_by(pharmacy_id=pharmacy_id, medication_id=medication.medication_id).first()
        if not inventory_item:
            raise ValueError("Medication not found in the pharmacy inventory")
        if status == PrescriptionStatus.PAID:
            inventory_item.quantity -= medication.dosage * medication.duration
            if inventory_item.quantity < 0:
                raise ValueError("Not enough medication in the inventory")
        elif status == PrescriptionStatus.UNPAID:
            inventory_item.quantity += medication.dosage * medication.duration
        else:
            raise ValueError("Invalid status")
    db.session.commit()
    return get_pharmacy_medications_inventory(pharmacy_id)

def update_prescription_status(prescription_id, status_str: str):
    prescription = Prescription.query.get(prescription_id)
    if not prescription:
        raise ValueError("Prescription not found")
    if isinstance(status_str, str):
        try:
            status = PrescriptionStatus(status_str.lower())
        except ValueError:
            raise ValueError(f"Invalid status: {status_str}")
    if prescription.status == status:
        raise ValueError("Prescription already has the requested status")
    else:
        try:
            update_medication_inventory(prescription_id, status)
        except ValueError as e:
            raise ValueError(f"Failed to update medication inventory: {str(e)}")

    prescription.status = status
    db.session.commit()
    return prescription.to_dict()