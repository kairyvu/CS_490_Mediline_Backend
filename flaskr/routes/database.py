from flask import Blueprint, jsonify
from flaskr.models import User, Patient, Doctor, Pharmacy, SuperUser, Post, Comment, Report, PatientReport, RatingSurvey, Invoice, Notification, MedicalRecord, Prescription, PrescriptionMedication, Medication, Inventory, ExerciseBank, PatientExercise, Chat, Message, UserAudit, PatientAudit, DoctorAudit, AppointmentAudit, Appointment, AppointmentDetail

database_bp = Blueprint("database", __name__)

@database_bp.route('/', methods=['GET'])
def fetch_tables():
    patients = Patient.query.all()
    patients_list = [patient.to_dict() for patient in patients]
    return jsonify(patients_list)