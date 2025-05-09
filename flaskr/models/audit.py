from flaskr.extensions import db
from flaskr.struct import Action, AccountType

class UserAudit(db.Model):
    __tablename__ = 'user_audit'

    audit_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    username_old = db.Column(db.String(80), nullable=False)
    username_new = db.Column(db.String(80), nullable=False)
    password_old = db.Column(db.String(255), nullable=False)
    password_new = db.Column(db.String(255), nullable=False)
    account_type_old = db.Column(db.Enum(AccountType), nullable=False)
    account_type_new = db.Column(db.Enum(AccountType), nullable=False)
    created_at_old = db.Column(db.DateTime, server_default=db.func.now())
    created_at_new = db.Column(db.DateTime, server_default=db.func.now())
    updated_at_old = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    updated_at_new = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    action = db.Column(db.Enum(Action), nullable=False)
    audit_timestamp = db.Column(db.DateTime, server_default=db.func.now())
    audit_user = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

class DoctorAudit(db.Model):
    __tablename__ = 'doctor_audit'

    audit_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    first_name_old = db.Column(db.String(80), nullable=False)
    first_name_new = db.Column(db.String(80), nullable=False)
    last_name_old = db.Column(db.String(80), nullable=False)
    last_name_new = db.Column(db.String(80), nullable=False)
    email_old = db.Column(db.String(120), unique=True, nullable=False)
    email_new = db.Column(db.String(120), unique=True, nullable=False)
    phone_old = db.Column(db.String(20), nullable=False)
    phone_new = db.Column(db.String(20), nullable=False)
    specialization_old = db.Column(db.String(80), nullable=False)
    specialization_new = db.Column(db.String(80), nullable=False)
    bio_old = db.Column(db.Text, nullable=True)
    bio_new = db.Column(db.Text, nullable=True)
    fee_old = db.Column(db.Float, nullable=False)
    fee_new = db.Column(db.Float, nullable=False)
    profile_picture_old = db.Column(db.String(120), nullable=True)
    profile_picture_new = db.Column(db.String(120), nullable=True)
    dob_old = db.Column(db.Date, nullable=False)
    dob_new = db.Column(db.Date, nullable=False)
    license_id_old = db.Column(db.String(80), unique=True, nullable=False)
    license_id_new = db.Column(db.String(80), unique=True, nullable=False)
    action = db.Column(db.Enum(Action), nullable=False)
    audit_timestamp = db.Column(db.DateTime, server_default=db.func.now())
    audit_user = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

class PatientAudit(db.Model):
    __tablename__ = 'patient_audit'

    audit_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    first_name_old = db.Column(db.String(80), nullable=False)
    first_name_new = db.Column(db.String(80), nullable=False)
    last_name_old = db.Column(db.String(80), nullable=False)
    last_name_new = db.Column(db.String(80), nullable=False)
    email_old = db.Column(db.String(120), unique=True, nullable=False)
    email_new = db.Column(db.String(120), unique=True, nullable=False)
    phone_old = db.Column(db.String(20), nullable=False)
    phone_new = db.Column(db.String(20), nullable=False)
    dob_old = db.Column(db.Date, nullable=False)
    dob_new = db.Column(db.Date, nullable=False)
    doctor_id_old = db.Column(db.Integer, db.ForeignKey('doctor.user_id'), nullable=False)
    doctor_id_new = db.Column(db.Integer, db.ForeignKey('doctor.user_id'), nullable=False)
    pharmacy_id_old = db.Column(db.Integer, db.ForeignKey('pharmacy.user_id'), nullable=False)
    pharmacy_id_new = db.Column(db.Integer, db.ForeignKey('pharmacy.user_id'), nullable=False)
    action = db.Column(db.Enum(Action), nullable=False)
    audit_timestamp = db.Column(db.DateTime, server_default=db.func.now())
    audit_user = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

class AppointmentAudit(db.Model):
    __tablename__ = 'appointment_audit'

    audit_id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.appointment_id'), nullable=False)
    patient_id_old = db.Column(db.Integer, db.ForeignKey('patient.user_id'), nullable=False)
    patient_id_new = db.Column(db.Integer, db.ForeignKey('patient.user_id'), nullable=False)
    doctor_id_old = db.Column(db.Integer, db.ForeignKey('doctor.user_id'), nullable=False)
    doctor_id_new = db.Column(db.Integer, db.ForeignKey('doctor.user_id'), nullable=False)
    created_at_old = db.Column(db.DateTime, nullable=False)
    created_at_new = db.Column(db.DateTime, nullable=False)
    updated_at_old = db.Column(db.DateTime, nullable=False)
    updated_at_new = db.Column(db.DateTime, nullable=False)
    action = db.Column(db.Enum(Action), nullable=False)
    audit_timestamp = db.Column(db.DateTime, server_default=db.func.now())
    audit_user = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
