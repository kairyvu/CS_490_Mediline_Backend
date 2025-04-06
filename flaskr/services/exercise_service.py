from flaskr.models import ExerciseBank, PatientExercise

def get_exercises(sort_by='exercise_id', order='asc'):
    if not hasattr(ExerciseBank, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    
    column = getattr(ExerciseBank, sort_by)
    if order == 'desc':
        column = column.desc()
    exercises = ExerciseBank.query.order_by(column).all()
    return [exercise.to_dict() for exercise in exercises]

def get_user_exercise(user_id, sort_by='exercise_id', order='asc'):
    if not hasattr(PatientExercise, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    
    column = getattr(PatientExercise, sort_by)
    if order == 'desc':
        column = column.desc()
    exercises = PatientExercise.query.filter_by(patient_id=user_id).order_by(column).all()
    result = []
    for ex in exercises:
        ex_dict = ex.to_dict()
        if ex.exercise:
            ex_dict['type_of_exercise'] = ex.exercise.type_of_exercise
            ex_dict['description'] = ex.exercise.description
        result.append(ex_dict)
    return result