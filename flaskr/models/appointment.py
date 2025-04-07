from flaskr.extensions import db
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

class AppointmentDetail(db.Model):
    __tablename__ = 'appointment_detail'

    appointment_details_id = db.Column(db.Integer, db.ForeignKey('appointment.appointment_id'), primary_key=True, nullable=False)
    treatment = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.PENDING)

    appointment = db.relationship('Appointment', backref=db.backref('appointment_detail', uselist=False))

    def to_dict(self):
        result = {
            'appointment_id': self.appointment_details_id,
            'treatment': self.treatment,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status.name
        }
        if self.appointment:
            result['doctor_id'] = self.appointment.doctor_id
            result['patient_id'] = self.appointment.patient_id

            if self.appointment.doctor:
                result['doctor_name'] = f"{self.appointment.doctor.first_name} {self.appointment.doctor.last_name}"
                result['fee'] = self.appointment.doctor.fee
            else:
                result['doctor_name'] = None

            if self.appointment.patient:
                result['patient_name'] = f"{self.appointment.patient.first_name} {self.appointment.patient.last_name}"
            else:
                result['patient_name'] = None

        return result