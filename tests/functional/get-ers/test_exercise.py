import pytest
from flaskr.services import get_all_patient_exercise, get_exercises
from flaskr.models import PatientExercise, ExerciseBank, Doctor, Patient, User
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

def test_get_all_patient_exercises(database_session, pt_ex1, pt_ex2, pt_ex3):
    db = database_session
    db.metadata.create_all(db.engine, [
        PatientExercise.__table__,
        ExerciseBank.__table__,
        Doctor.__table__,
        Patient.__table__,
        User.__table__
    ])
    _pt_ex1, pt1, dr1, ex1 = pt_ex1
    _pt_ex2, _, _, ex2 = pt_ex2
    _pt_ex3, _, _, ex3 = pt_ex3
    u1, p1 = pt1
    u2, d1 = dr1
    db.session.add_all([u1, u2, p1, d1, ex1, ex2, ex3])
    db.session.flush()
    db.session.add_all([_pt_ex1, _pt_ex2, _pt_ex3])
    db.session.flush()
    res1 = get_all_patient_exercise(u1.user_id)
    assert isinstance(res1, list)

    res2 = get_all_patient_exercise(u1.user_id, sort_by='reps')
    # Check sorting was correct
    assert res2[0]['reps'] < res2[1]['reps']

    db.session.rollback()
    db.metadata.drop_all(db.engine)

def test_get_exercises_table_not_found(database_session):
    with pytest.raises(Exception):
        get_exercises()
