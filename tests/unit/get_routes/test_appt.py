import pytest
from flaskr.services.appointment_service import get_appointment, get_upcoming_appointments

def test_get_upcoming_appt_not_found(database_session):
    with pytest.raises(ValueError):
        get_upcoming_appointments(1)

def test_get_upcoming_appt(database_session, appt1):
    _p, _d, _appt, _appt_dt = appt1
    _up, _pt = _p
    _ud, _dr = _d
    db = database_session
    db.session.add_all([_up, _ud, _pt, _dr, _appt, _appt_dt])
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

def test_get_appt_not_found(database_session):
    with pytest.raises(ValueError):
        get_upcoming_appointments(1)

def test_get_appt(database_session, appt1):
    _p, _d, _appt, _appt_dt = appt1
    _up, _pt = _p
    _ud, _dr = _d
    db = database_session
    db.session.add_all([_up, _ud, _pt, _dr, _appt, _appt_dt])
    db.session.flush()
    res = get_appointment(1)
    assert res is not None
    db.session.rollback()
