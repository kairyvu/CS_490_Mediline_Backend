from flaskr.extensions import db

class PatientRequest(db.Model):
    __tablename__ = 'patient_request'

    request_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.user_id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    patient = db.relationship('Patient', backref=db.backref('requests', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('requests', lazy=True))

    def to_dict(self):
        return {
            "request_id": self.request_id,
            "doctor_id": self.doctor_id,
            "patient_id": self.patient_id,
            "request_date": self.created_at.isoformat() if self.created_at else None
        }
