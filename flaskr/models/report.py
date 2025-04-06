from flaskr import db
from flaskr.struct import ReportType

class Report(db.Model):
    __tablename__ = 'report'

    report_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(ReportType), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, type):
        self.type = type
    
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

    def __init__(self, report_id, patient_id, doctor_id, height=None, weight=None, calories_intake=None, hours_of_exercise=None, hours_of_sleep=None):
        self.report_id = report_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.height = height
        self.weight = weight
        self.calories_intake = calories_intake
        self.hours_of_exercise = hours_of_exercise
        self.hours_of_sleep = hours_of_sleep

    def __repr__(self):
        return f'<Patientreport {self.report_id} {self.patient_id}>'