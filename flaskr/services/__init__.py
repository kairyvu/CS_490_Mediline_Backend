from functools import wraps
import jwt
from flask import request, Response, current_app, jsonify
from flask_jwt_extended.exceptions import JWTExtendedException
from flaskr.models import User

from .auth_service import user_id_credentials
from .exercise_service import get_exercises, get_all_patient_exercise, add_patient_exercise, update_patient_exercise
from .payment_service import get_invoices_by_user, update_invoice_status, assign_invoice_appoinmtnet, delete_invoice
from .appointment_service import get_upcoming_appointments, add_appointment, update_appointment, get_appointment
from .report_service import get_patient_report_result, add_patient_report
from .prescription_service import get_medications_by_prescription, get_prescriptions, get_prescription_count_by_pharmacy, get_pharmacy_medications_inventory, get_medications_history_by_patient, update_medication_inventory, update_prescription_status
from .chat_service import get_current_chat, add_message
from .social_media_service import get_all_posts, get_comments_of_post, delete_comment, delete_post, update_comment, update_post, create_comment, create_post
from .doctor_service import all_doctors, doctor_details, upcoming_appointments_count, pending_appointments_count,\
    doctor_patients_count_and_list, todays_patient, doctor_rating_detail, last_completed_appointment, doctor_general_discussion, \
    new_appointments_request, update_doctor, assign_survey
from .pharmacy_service import get_all_pharmacy_patients, add_pt_rx, get_pharmacy_info, validate_rx
from .patient_service import patient_info, update_patient, update_primary_pharmacy, update_doctor_by_patient_id
from .registration_service import add_user
from .medication_service import medication_info
from .user_service import get_user_info_by_id
from .request_service import add_patient_request, delete_patient_request, get_patient_requests_by_user_id
from .medical_record_service import get_medical_records_by_user, create_medical_record, update_medical_record, delete_medical_record


__all__ = [
    'user_id_credentials',
    'get_exercises', 'get_all_patient_exercise', 'add_patient_exercise', 'update_patient_exercise',
    'get_invoices_by_user', 'update_invoice_status', 'assign_invoice_appoinmtnet', 'delete_invoice',
    'get_upcoming_appointments', 'add_appointment', 'update_appointment', 'get_appointment',
    'get_patient_report_result', 'add_patient_report',
    'get_medications_by_prescription', 'get_prescriptions',
    'get_prescription_count_by_pharmacy', 'get_pharmacy_medications_inventory', 'get_medications_history_by_patient', 'update_prescription_status',
    'get_current_chat', 'add_message', 
    'get_all_posts', 'get_comments_of_post', 'delete_comment', 'delete_post', 'update_comment', 'update_post', 'create_comment', 'create_post',
    'all_doctors', 'doctor_details', 'upcoming_appointments_count', 'pending_appointments_count', 'doctor_patients_count_and_list', 'todays_patient', 'doctor_rating_detail', 'last_completed_appointment', 'doctor_general_discussion', 'get_all_pharmacy_patients', 'get_pharmacy_info', 'add_pt_rx', 'validate_rx',
    'patient_info', 'update_patient','patient_medical_history', 'create_medical_record', 'update_primary_pharmacy', 'update_doctor_by_patient_id',
    'add_user', 'new_appointments_request', 'update_doctor', 'assign_survey',
    'medication_info',
    'get_user_info_by_id',
    'add_patient_request', 'delete_patient_request', 'get_patient_requests_by_user_id',
    'get_medical_records_by_user', 'create_medical_record', 'update_medical_record', 'delete_medical_record'
]

# AUTHORIZATION EXCEPTION RESPONSES
class UnauthorizedError(JWTExtendedException):
    pass

def USER_NOT_AUTHORIZED(uid: int|None=None) -> Response:
    if uid:
        return jsonify({
            'error': f'User with id {uid} does not have permission to this resource'
        }), 401
    return jsonify({'error': 'User does not have permission to this resource'}), 401
   
