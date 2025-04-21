from flaskr.extensions import db
from flaskr.struct import ReportType

class Report(db.Model):
    __tablename__ = 'report'

    report_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(ReportType), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
class PatientReport(db.Model):
    __tablename__ = 'patient_report'

    patient_report_id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.report_id', ondelete='CASCADE'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.user_id', ondelete='CASCADE'), nullable=False)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    calories_intake = db.Column(db.Integer, nullable=True)
    hours_of_exercise = db.Column(db.Integer, nullable=True)
    hours_of_sleep = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    report = db.relationship('Report', backref='patient_reports', lazy=True)
    patient = db.relationship('Patient', backref='patient_reports', lazy=True)
    doctor = db.relationship('Doctor', backref='patient_reports', lazy=True)

    def to_dict(self):
        return {
            'patient_report_id': self.patient_report_id,
            'report_id': self.report_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'height': self.height,
            'weight': self.weight,
            'calories_intake': self.calories_intake,
            'hours_of_exercise': self.hours_of_exercise,
            'hours_of_sleep': self.hours_of_sleep,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }