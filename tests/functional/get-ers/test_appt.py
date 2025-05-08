from datetime import datetime
import pytest
from werkzeug.datastructures import ImmutableMultiDict
from flaskr.services import add_user, get_appointment, get_upcoming_appointments, \
    add_patient_request, delete_patient_request, update_doctor_by_patient_id, \
    user_id_credentials, add_appointment
from flaskr.models import Country, City, Address, User, Patient, Doctor, Appointment, AppointmentDetail, PatientRequest

def test_get_upcoming_appt_not_found(database_session):
    db = database_session
    db.metadata.create_all(db.engine, [
        User.__table__,
        Patient.__table__,
        Doctor.__table__,
    ])
    with pytest.raises(ValueError):
        get_upcoming_appointments(1)
    db.metadata.drop_all(db.engine)

def test_get_upcoming_appt(database_session, pt_reg_form1, dr_reg_form1):
    db = database_session
    db.metadata.create_all(db.engine, [
        Country.__table__,
        City.__table__,
        Address.__table__,
        User.__table__,
        Doctor.__table__,
        Patient.__table__,
        Appointment.__table__,
        AppointmentDetail.__table__,
        PatientRequest.__table__
    ])
    id1 = add_user(ImmutableMultiDict(list(pt_reg_form1.items()))) \
            .get_json().get('user_id')
    id2 = add_user(ImmutableMultiDict(list(dr_reg_form1.items()))) \
            .get_json().get('user_id')
    assert isinstance(id1, int)
    assert isinstance(id2, int)
    assert id1 != id2
    pt1_tok = user_id_credentials(pt_reg_form1['username'], 
                                  pt_reg_form1['password']).get('token')
    dr1_tok = user_id_credentials(dr_reg_form1['username'], 
                                  dr_reg_form1['password']).get('token')
    assert pt1_tok != dr1_tok
    req = add_patient_request(id1, id2)
    assert isinstance(req, dict)
    res = delete_patient_request(req['request_id'], (doc := User.query.filter_by(user_id=id2).first()))
    assert isinstance(res, dict)
    pt = update_doctor_by_patient_id(res['patient_id'], res['doctor_id'], doc)
    assert isinstance(pt, dict)
    appt = add_appointment(pt['doctor_id'], pt['user_id'], 'consult', datetime(2000, 3, 1))
    assert isinstance(appt, int)
    pt_appt = get_upcoming_appointments(id1)
    dr_appt = get_upcoming_appointments(id2)
    assert isinstance(pt_appt, list)
    assert pt_appt == dr_appt
    assert {'appointment_id', 'treatment', 'patient_id', 'doctor_id'} <= set(pt_appt[0])

def test_get_appt_not_found(database_session):
    db = database_session
    db.metadata.create_all(db.engine, [
        AppointmentDetail.__table__
    ])
    with pytest.raises(ValueError):
        get_appointment(1)
    db.metadata.drop_all(db.engine)

def test_get_appt(database_session, pt_reg_form1, dr_reg_form1):
    # Setup: Create appt
    db = database_session
    db.metadata.create_all(db.engine, [
        Country.__table__,
        City.__table__,
        Address.__table__,
        User.__table__,
        Doctor.__table__,
        Patient.__table__,
        Appointment.__table__,
        AppointmentDetail.__table__,
        PatientRequest.__table__
    ])
    id1 = add_user(ImmutableMultiDict(list(pt_reg_form1.items()))) \
            .get_json().get('user_id')
    id2 = add_user(ImmutableMultiDict(list(dr_reg_form1.items()))) \
            .get_json().get('user_id')
    assert isinstance(id1, int)
    assert isinstance(id2, int)
    assert id1 != id2
    pt1_tok = user_id_credentials(pt_reg_form1['username'], 
                                  pt_reg_form1['password']).get('token')
    dr1_tok = user_id_credentials(dr_reg_form1['username'], 
                                  dr_reg_form1['password']).get('token')
    assert pt1_tok != dr1_tok
    req = add_patient_request(id1, id2)
    assert isinstance(req, dict)
    res = delete_patient_request(req['request_id'], (doc := User.query.filter_by(user_id=id2).first()))
    assert isinstance(res, dict)
    pt = update_doctor_by_patient_id(res['patient_id'], res['doctor_id'], doc)
    assert isinstance(pt, dict)
    appt = add_appointment(pt['doctor_id'], pt['user_id'], 'consult', datetime(2000, 3, 1))
    assert isinstance(appt, int)
    pt_appt = get_upcoming_appointments(id1)
    dr_appt = get_upcoming_appointments(id2)
    assert isinstance(pt_appt, list)
    assert pt_appt == dr_appt
    assert {'appointment_id', 'treatment', 'patient_id', 'doctor_id'} <= set(pt_appt[0])
    # Test get appt detail
    res2 = get_appointment(appt)
    assert isinstance(res2, dict)
    assert {'appointment_id', 'treatment', 'patient_id', 'doctor_id'} <= set(res2)
