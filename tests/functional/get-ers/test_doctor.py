import pytest
from flaskr.services.doctor_service import all_doctors, doctor_details, todays_patient
from flaskr.models import User, Doctor

def test_all_doctors_table_not_exist(database_session):
    with pytest.raises(Exception):
        all_doctors()

def test_all_doctors_empty_table(database_session):
    db = database_session
    db.metadata.create_all(db.engine, [
        Doctor.__table__
    ])
    res = all_doctors()
    assert isinstance(res, list)
    assert len(res) == 0
    db.metadata.drop_all(db.engine)

def test_all_doctors(database_session):
    db = database_session
    db.metadata.create_all(db.engine, [
        Doctor.__table__
    ])
    res = all_doctors()
    assert isinstance(res, list)
    assert len(res) == 0
    db.metadata.drop_all(db.engine)

def test_get_doctor_info(database_session, dr1):
    db = database_session
    db.metadata.create_all(db.engine, [
        User.__table__,
        Doctor.__table__
    ])
    user, user_dr = dr1
    db.session.add_all([user, user_dr])                                         
    db.session.flush()
    res = doctor_details(2)
    assert isinstance(res, dict)
    assert {
        "user_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "specialization",
        "bio",
        "fee",
        "profile_picture",
        "dob",
        "license_id"
    } <= set(res)
    db.session.rollback()
    db.metadata.drop_all(db.engine)

def test_get_doctor_info_not_found(database_session):
    with pytest.raises(Exception) as e:
        doctor_details(1)

def test_get_doctor_info_not_found_2(database_session):
    from flaskr.models import Doctor
    db = database_session
    db.metadata.create_all(db.engine, [
        Doctor.__table__
    ])
    res = doctor_details(2)
    assert res is None
    db.metadata.drop_all(db.engine)

def test_todays_patient_table_not_exist(database_session):
    with pytest.raises(Exception):
        todays_patient()

def test_todays_patient_bad_date(database_session):
    res1 = todays_patient(1, 'laksdjsflkajs')
    assert 'error' in res1
    assert res1['error'] == 'Invalid date format. Use YYYY-MM-DD.'

    with pytest.raises(TypeError):
        res2 = todays_patient(1, 1)