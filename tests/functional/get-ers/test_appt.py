import pytest
from flaskr.services import get_appointment, get_upcoming_appointments
from flaskr.models import Country, City, Address, User, Patient, Doctor, Appointment, AppointmentDetail

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

def test_get_upcoming_appt(database_session, appt1):
    db = database_session
    db.metadata.create_all(db.engine, [
        Country.__table__,
        City.__table__,
        Address.__table__,
        User.__table__,
        Patient.__table__,
        Doctor.__table__,
        Appointment.__table__,
        AppointmentDetail.__table__
    ])
    _p, _d, _appt, _appt_dt = appt1
    _up, _pt = _p
    _ud, _dr = _d
    db.session.add_all([_up, _ud, _pt, _dr])
    db.session.flush()
    db.session.add_all([_appt, _appt_dt])
    db.session.flush()
    res = get_upcoming_appointments(1)
    assert isinstance(res, list)
    assert {
        'appointment_id',
        'treatment',
        'start_date', 
        'end_date', 
        'status', 
    } <= set(res[0])
    db.session.rollback()
    db.metadata.drop_all(db.engine)

def test_get_appt_not_found(database_session):
    db = database_session
    db.metadata.create_all(db.engine, [
        AppointmentDetail.__table__
    ])
    with pytest.raises(ValueError):
        get_appointment(1)
    db.metadata.drop_all(db.engine)

def test_get_appt(database_session, appt1):
    db = database_session
    db.metadata.create_all(db.engine, [
        User.__table__,
        Patient.__table__,
        Doctor.__table__,
        Appointment.__table__,
        AppointmentDetail.__table__
    ])
    _p, _d, _appt, _appt_dt = appt1
    _up, _pt = _p
    _ud, _dr = _d
    db = database_session
    db.session.add_all([_up, _ud, _pt, _dr, _appt, _appt_dt])
    db.session.flush()
    res = get_appointment(1)
    assert res is not None
    db.session.rollback()
    db.metadata.drop_all(db.engine)
