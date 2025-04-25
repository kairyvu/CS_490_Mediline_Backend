from flaskr.models import ExerciseBank, PatientExercise, Patient, Doctor
def test_exercise(ex1):
    assert ex1.exercise_id == 1
    assert isinstance(ex1, ExerciseBank)

def test_patient_exercise(pt_ex1):
    assert isinstance(pt_ex1, PatientExercise)
    assert isinstance(pt_ex1.exercise, ExerciseBank)
    assert isinstance(pt_ex1.patient, Patient)
    assert isinstance(pt_ex1.doctor, Doctor)
