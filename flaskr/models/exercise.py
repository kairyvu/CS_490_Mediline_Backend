from flaskr import db

class ExerciseBank(db.Model):
    __tablename__ = 'exercise_bank'

    exercise_id = db.Column(db.Integer, primary_key=True)
    type_of_exercise = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __init__(self, type_of_exercise, description):
        self.type_of_exercise = type_of_exercise
        self.description = description

class PatientExercise(db.Model):
    __tablename__ = 'patient_exercise'

    patient_exercise_id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise_bank.exercise_id', ondelete='CASCADE'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.user_id', ondelete='CASCADE'), nullable=False)
    reps = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, exercise_id, patient_id, doctor_id, reps):
        self.exercise_id = exercise_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.reps = reps

    def __repr__(self):
        return f'<PatientExercise {self.exercise_id} {self.patient_id}>'
