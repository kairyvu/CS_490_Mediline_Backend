from flaskr.extensions import db

class ExerciseBank(db.Model):
    __tablename__ = 'exercise_bank'

    exercise_id = db.Column(db.Integer, primary_key=True)
    type_of_exercise = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "exercise_id": self.exercise_id,
            "type_of_exercise": self.type_of_exercise,
            "description": self.description
        }

class PatientExercise(db.Model):
    __tablename__ = 'patient_exercise'

    patient_exercise_id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise_bank.exercise_id', ondelete='CASCADE'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.user_id', ondelete='CASCADE'), nullable=False)
    reps = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    exercise = db.relationship('ExerciseBank', backref='patient_exercises', lazy=True)
    patient = db.relationship('Patient', backref='patient_exercises', lazy=True)
    doctor = db.relationship('Doctor', backref='patient_exercises', lazy=True)

    def to_dict(self):
        return {
            "patient_exercise_id": self.patient_exercise_id,
            "exercise_id": self.exercise_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "reps": self.reps,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
