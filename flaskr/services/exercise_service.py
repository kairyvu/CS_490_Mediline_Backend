from flaskr.models import User, ExerciseBank, PatientExercise
from flaskr.struct import ExerciseStatus
from flaskr.extensions import db

from sqlalchemy.exc import IntegrityError   # For exception handling (foreign key constraint failure)

def get_exercises(sort_by='exercise_id', order='asc'):
    if not hasattr(ExerciseBank, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    
    column = getattr(ExerciseBank, sort_by)
    if order == 'desc':
        column = column.desc()
    exercises = ExerciseBank.query.order_by(column).all()
    return [exercise.to_dict() for exercise in exercises]

def get_all_patient_exercise(user_id, sort_by='exercise_id', order='asc'):
    if not hasattr(PatientExercise, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    
    column = getattr(PatientExercise, sort_by)
    if order.lower() == 'desc':
        column = column.desc()
    elif order.lower() == 'asc':
        column = column.asc()
    else:
        raise ValueError(f"Invalid order: {order}")
    exercises = PatientExercise.query.filter_by(patient_id=user_id).order_by(column).all()
    result = []
    for ex in exercises:
        ex_dict = ex.to_dict()
        if ex.exercise:
            ex_dict['type_of_exercise'] = ex.exercise.type_of_exercise
            ex_dict['description'] = ex.exercise.description
        result.append(ex_dict)
    return result

def add_patient_exercise(exercise_id, patient_id, doctor_id, reps):
    exercise = PatientExercise(
        exercise_id=exercise_id,
        patient_id=patient_id,
        doctor_id=doctor_id,
        reps=reps,
        status=ExerciseStatus.IN_PROGRESS
    )
    db.session.add(exercise)
    try:
        db.session.commit()
    except IntegrityError as e:
        raise e
    # Successful commit; return the created entry id
    return exercise.patient_exercise_id
    

def update_patient_exercise(exercise_id, status, reps, 
                            requesting_user: User|None=None):
    from flaskr.services import UnauthorizedError
    exercise = PatientExercise.query.filter_by(patient_exercise_id=exercise_id).first()
    if not exercise:
        raise ValueError("Exercise not found")
    
    if requesting_user:
        match requesting_user.account_type.name:
            case 'SuperUser' | 'Patient' \
                if exercise.patient_id == requesting_user.user_id:
                pass
            case _:
                return UnauthorizedError
    else:
        return UnauthorizedError
    if not reps:
        raise ValueError("reps is required")
    if not status:
        raise ValueError("status is required")
    exercise.reps = reps
    exercise.status = status
    db.session.commit()