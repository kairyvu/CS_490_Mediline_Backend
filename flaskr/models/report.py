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