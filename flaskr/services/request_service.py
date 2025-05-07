from flaskr.models import PatientRequest
from flaskr.extensions import db

def add_patient_request(patient_id, doctor_id):
    new_request = PatientRequest(patient_id=patient_id, doctor_id=doctor_id)
    db.session.add(new_request)
    db.session.commit()
    return new_request.to_dict()

def delete_patient_request(request_id):
    request = PatientRequest.query.filter_by(request_id=request_id).first()
    if not request:
        return None
    db.session.delete(request)
    db.session.commit()
    return request.to_dict()

def get_patient_requests_by_doctor_id(doctor_id, sort_by='created_at', order='desc'):
    if not hasattr(PatientRequest, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    column = getattr(PatientRequest, sort_by)
    if order.lower() == 'desc':
        column = column.desc()
    elif order.lower() == 'asc':
        column = column.asc()
    else:
        raise ValueError(f"Invalid order: {order}")
    requests = PatientRequest.query.filter_by(doctor_id=doctor_id).order_by(column).all()
    return [request.to_dict() for request in requests]