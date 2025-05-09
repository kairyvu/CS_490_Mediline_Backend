from flaskr.models import Patient, PatientRequest, Doctor
from flaskr.extensions import db

def add_patient_request(patient_id, doctor_id):
    if (PatientRequest.query
        .filter_by(patient_id=patient_id, doctor_id=doctor_id)
        .first()):
        raise ValueError(f'patient with ID: {patient_id} already requested doctor with ID: {doctor_id}')
    if (Patient.query
        .filter_by(user_id=patient_id)
        .first().doctor_id == doctor_id):
        raise ValueError(f'patient with ID: {patient_id} is already assigned doctor with ID: {doctor_id}')
    requested_doc = Doctor.query.filter_by(user_id=doctor_id).first()
    if not requested_doc:
        raise ValueError(f'Doctor not found')
    if not requested_doc.accepting_patients:
        raise ValueError(f'Doctor is not accepting patients at the moment')
    new_request = PatientRequest(patient_id=patient_id, doctor_id=doctor_id)
    db.session.add(new_request)
    db.session.commit()
    return new_request.to_dict()

def delete_patient_request(request_id, requesting_user=None):
    from flaskr.services import UnauthorizedError
    if not requesting_user:
        raise UnauthorizedError
    request = PatientRequest.query.filter_by(request_id=request_id).first()
    if not request:
        return None
    if not (requesting_user.account_type.name != 'SUPERUSER' 
            and request.doctor_id == requesting_user.user_id):
        raise UnauthorizedError

    db.session.delete(request)
    db.session.commit()
    return request.to_dict()

def get_patient_requests_by_user_id(user_id, sort_by='created_at', order='desc'):
    is_doctor = Doctor.query.filter_by(user_id=user_id).first()
    is_patient = Patient.query.filter_by(user_id=user_id).first()
    if not is_doctor and not is_patient:
        raise ValueError(f'User with ID: {user_id} is neither a doctor nor a patient')
    if not hasattr(PatientRequest, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    column = getattr(PatientRequest, sort_by)
    if order.lower() == 'desc':
        column = column.desc()
    elif order.lower() == 'asc':
        column = column.asc()
    else:
        raise ValueError(f"Invalid order: {order}")
    if is_doctor:
        requests = PatientRequest.query.filter_by(doctor_id=user_id).order_by(column).all()
    elif is_patient:
        requests = PatientRequest.query.filter_by(patient_id=user_id).order_by(column).all()
    return [request.to_dict() for request in requests]