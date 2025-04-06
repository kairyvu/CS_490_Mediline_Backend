from flask import Blueprint
from flaskr.models import User, Patient, Doctor, Pharmacy, SuperUser, Post, Comment, Report, PatientReport, RatingSurvey, Invoice, Notification, MedicalRecord, Prescription, PrescriptionMedication, Medication, Inventory, ExerciseBank, PatientExercise, Chat, Message, UserAudit, PatientAudit, DoctorAudit, AppointmentAudit, Appointment, AppointmentDetail

database_bp = Blueprint("database", __name__)

@database_bp.route('/', methods=['GET'])
def fetch_tables():
    return Patient.query.all()
