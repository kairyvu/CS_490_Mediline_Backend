import pytest
from flaskr.services.doctor_service import all_doctors, doctor_details

def test_all_doctors_table_not_exist(database_session):
    with pytest.raises(Exception):
        all_doctors()

def test_all_doctors_empty_table(database_session):
    from flaskr.models import Doctor
    db = database_session
    db.metadata.create_all(db.engine, [
        Doctor.__table__
    ])
    res = all_doctors()
    assert isinstance(res, list)
    assert len(res) == 0
    db.metadata.drop_all(db.engine)

def test_all_doctors(database_session):
    from flaskr.models import Doctor
    db = database_session
    db.metadata.create_all(db.engine, [
        Doctor.__table__
    ])
    res = all_doctors()
    assert isinstance(res, list)
    assert len(res) == 0
    db.metadata.drop_all(db.engine)

def test_get_doctor_info(database_session, dr1):
    from flaskr.models import User, Doctor
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