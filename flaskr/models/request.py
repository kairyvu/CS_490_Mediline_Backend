from flaskr.extensions import db

class PatientRequest(db.Model):
    __tablename__ = 'patient_request'

    request_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient'), nullable=False)
    request_date = db.Column(db.DateTime, nullable=False)

    patient = db.relationship('Patient', backref=db.backref('requests', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('requests', lazy=True))

    def to_dict(self):
        return {
            "request_id": self.request_id,
            "doctor_id": self.doctor_id,
            "patient_id": self.patient_id,
            "request_date": self.request_date.isoformat() if self.request_date else None
        }