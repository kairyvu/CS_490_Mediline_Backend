import pytest
from flaskr.services import get_all_patient_exercise, get_exercises
from flaskr.struct import ExerciseStatus
def test_get_all_patient_exercises_table_not_found(database_session):
    with pytest.raises(Exception):
        get_all_patient_exercise(1)

def test_get_all_patient_exercises_no_result(database_session):
    from flaskr.models import PatientExercise
    db = database_session
    db.metadata.create_all(db.engine, [
        PatientExercise.__table__
    ])
    res = get_all_patient_exercise(1)
    assert isinstance(res, list)
    assert len(res) == 0
    db.metadata.drop_all(db.engine)

def test_get_all_patient_exercises_bad_sort(database_session):
    from flaskr.models import PatientExercise
    db = database_session
    db.metadata.create_all(db.engine, [
        PatientExercise.__table__
    ])
    bad_field = 'alkjsdblkj'
    with pytest.raises(ValueError) as e:
        res = get_all_patient_exercise(1, sort_by=bad_field)
    assert bad_field in str(e)
    db.metadata.drop_all(db.engine)

def test_get_all_patient_exercises(database_session, pt_ex1, ex2, ex3):
    from flaskr.models import PatientExercise, ExerciseBank, Doctor, Patient, User
    db = database_session
    db.metadata.create_all(db.engine, [
        PatientExercise.__table__,
        ExerciseBank.__table__,
        Doctor.__table__,
        Patient.__table__,
        User.__table__
    ])
    pt_ex, pt1, dr1, ex1 = pt_ex1
    u1, p1 = pt1
    u2, d1 = dr1
    db.session.add_all([u1, u2, p1, d1, ex1, pt_ex, ex2, ex3])
    db.session.flush()
    res1 = get_all_patient_exercise(u1.user_id)
    assert isinstance(res1, list)

    pt_ex2 = PatientExercise(
        exercise_id=ex2.exercise_id,
        patient_id=u1.user_id,
        doctor_id=u2.user_id,
        reps='4-8',
        status=ExerciseStatus.IN_PROGRESS
    )
    pt_ex3 = PatientExercise(
        exercise_id=ex3.exercise_id,
        patient_id=u1.user_id,
        doctor_id=u2.user_id,
        reps='10min',
        status=ExerciseStatus.IN_PROGRESS
    )
    db.session.add_all([pt_ex2, pt_ex3])
    db.session.flush()

    res2 = get_all_patient_exercise(u1.user_id, sort_by='reps')
    # Check sorting was correct
    assert res2[0]['reps'] < res2[1]['reps']

    db.session.rollback()
    db.metadata.drop_all(db.engine)

def test_get_exercises_table_not_found(database_session):
    with pytest.raises(Exception):
        get_exercises()

def test_get_exercises_bad_sort(database_session):
    from flaskr.models import ExerciseBank
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
    from flaskr.models import ExerciseBank
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
    assert res2[0]['reps'] < res2[1]['reps']

    db.session.rollback()
    db.metadata.drop_all(db.engine)
