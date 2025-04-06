from flaskr import db
from flaskr.struct import AppointmentStatus

class Appointment(db.Model):
    __tablename__ = 'appointment'

    appointment_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.user_id', ondelete='CASCADE'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    doctor = db.relationship('Doctor', backref=db.backref('appointments', lazy=True))
    patient = db.relationship('Patient', backref=db.backref('appointments', lazy=True))

    def __init__ (self, doctor_id, patient_id):
        self.doctor_id = doctor_id
        self.patient_id = patient_id

class AppointmentDetail(db.Model):
    __tablename__ = 'appointment_detail'

    appointment_details_id = db.Column(db.Integer, db.ForeignKey('appointment.appointment_id'), primary_key=True, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.PENDING)
    
    def __init__(self, appointment_id, start_date, end_date, status=AppointmentStatus.PENDING):
        self.appointment_id = appointment_id
        self.start_date = start_date
        self.end_date = end_date
        self.status = status