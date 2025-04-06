from flaskr.extensions import db

class ExerciseBank(db.Model):
    __tablename__ = 'exercise_bank'

    exercise_id = db.Column(db.Integer, primary_key=True)
    type_of_exercise = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)

class PatientExercise(db.Model):
    __tablename__ = 'patient_exercise'

    patient_exercise_id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise_bank.exercise_id', ondelete='CASCADE'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.user_id', ondelete='CASCADE'), nullable=False)
    reps = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
