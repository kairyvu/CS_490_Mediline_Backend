import pytest
from flaskr.services import get_all_patient_exercise, get_exercises, add_user, add_patient_exercise, add_patient_request, update_doctor_by_patient_id, delete_patient_request
from flaskr.models import PatientExercise, ExerciseBank, Doctor, Patient, User, Address, City, Country, PatientRequest
def test_get_exercises_bad_sort(database_session):
    db = database_session
    db.metadata.create_all(db.engine, [
        ExerciseBank.__table__
    ])
    bad_field = 'alkjsdblkj'
    with pytest.raises(ValueError) as e:
        res = get_exercises(sort_by=bad_field)
    assert bad_field in str(e)
    db.metadata.drop_all(db.engine)

def test_get_exercises(database_session, ex1, ex2, ex3):
    db = database_session
    db.metadata.create_all(db.engine, [
        ExerciseBank.__table__,
    ])
    db.session.add_all([ex1, ex2, ex3])
    db.session.flush()
    res1 = get_exercises()
    assert isinstance(res1, list)

    res2 = get_exercises(sort_by='type_of_exercise')
    # Check sorting was correct
    assert res2[0]['type_of_exercise'] < res2[1]['type_of_exercise']

    db.session.rollback()
    db.metadata.drop_all(db.engine)
    
def test_get_all_patient_exercises_table_not_found(database_session):
    with pytest.raises(Exception):
        get_all_patient_exercise(1)

def test_get_all_patient_exercises_no_result(database_session):
    db = database_session
    db.metadata.create_all(db.engine, [
        PatientExercise.__table__
    ])
    res = get_all_patient_exercise(1)
    assert isinstance(res, list)
    assert len(res) == 0
    db.metadata.drop_all(db.engine)

def test_get_all_patient_exercises_bad_sort(database_session):
    db = database_session
    db.metadata.create_all(db.engine, [
        PatientExercise.__table__
    ])
    bad_field = 'alkjsdblkj'
    with pytest.raises(ValueError) as e:
        res = get_all_patient_exercise(1, sort_by=bad_field)
    assert bad_field in str(e)
    db.metadata.drop_all(db.engine)

def test_get_all_patient_exercises(database_session, pt_reg_form1, dr_reg_form1, ex1, ex2, ex3):
    from werkzeug.datastructures import ImmutableMultiDict
    db = database_session
    db.metadata.create_all(db.engine, [
        Country.__table__,
        City.__table__,
        Address.__table__,
        PatientExercise.__table__,
        ExerciseBank.__table__,
        Doctor.__table__,
        Patient.__table__,
        User.__table__,
        PatientRequest.__table__
    ])
    u1 = add_user(ImmutableMultiDict(list(pt_reg_form1.items()))).get_json()['user_id']
    u2 = add_user(ImmutableMultiDict(list(dr_reg_form1.items()))).get_json()['user_id']
    assert isinstance(u1, int)
    assert isinstance(u2, int)
    dr = User.query.filter_by(user_id=u2).first()
    pt = User.query.filter_by(user_id=u1).first()
    req = add_patient_request(u1, u2)['request_id']
    assert isinstance(req, int)
    update1 = delete_patient_request(req, dr)
    update2 = update_doctor_by_patient_id(u1, u2, dr)
    assert pt.patient.doctor_id == u2


def test_get_exercises_table_not_found(database_session):
    with pytest.raises(Exception):
        get_exercises()
