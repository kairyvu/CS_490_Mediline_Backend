from functools import wraps
import jwt
from flask import request, Response, current_app, jsonify
from flask_jwt_extended.exceptions import JWTExtendedException
from flaskr.models import User

from .auth_service import user_id_credentials
from .exercise_service import get_exercises, get_all_patient_exercise, add_patient_exercise, update_patient_exercise
from .payment_service import get_invoices_by_user, update_invoice_status, assign_invoice_appoinmtnet
from .appointment_service import get_upcoming_appointments, add_appointment, update_appointment, get_appointment
from .report_service import get_patient_report_result, add_patient_report
from .prescription_service import get_medications_by_prescription, get_prescriptions, get_prescription_count_by_pharmacy, get_pharmacy_medications_inventory, get_medications_history_by_patient
from .chat_service import get_current_chat, add_message
from .social_media_service import get_all_posts, get_comments_of_post, delete_comment, delete_post, update_comment, update_post, create_comment, create_post
from .doctor_service import all_doctors, doctor_details, total_patients, upcoming_appointments_count, pending_appointments_count, doctor_patients_count, todays_patient, doctor_rating_detail, last_completed_appointment, doctor_general_discussion, select_doctor, new_appointments_request, update_doctor
from .pharmacy_service import get_all_pharmacy_patients, add_pt_rx
from .patient_service import get_patient_info, patient_info, update_patient, patient_medical_history, create_medical_record, update_primary_pharmacy
from .registration_service import add_user
from .medication_service import medication_info

__all__ = [
    'user_id_credentials',
    'get_exercises', 'get_all_patient_exercise', 'add_patient_exercise', 'update_patient_exercise',
    'get_invoices_by_user', 'update_invoice_status', 'assign_invoice_appoinmtnet',
    'get_upcoming_appointments', 'add_appointment', 'update_appointment', 'get_appointment',
    'get_patient_report_result', 'add_patient_report',
    'get_medications_by_prescription', 'get_prescriptions',
    'get_prescription_count_by_pharmacy', 'get_pharmacy_medications_inventory', 'get_medications_history_by_patient',
    'get_current_chat', 'add_message', 
    'get_all_posts', 'get_comments_of_post', 'delete_comment', 'delete_post', 'update_comment', 'update_post', 'create_comment', 'create_post',
    'all_doctors', 'doctor_details', 'total_patients', 'upcoming_appointments_count', 'pending_appointments_count', 'doctor_patients_count', 'todays_patient', 'doctor_rating_detail', 'last_completed_appointment', 'doctor_general_discussion', 'select_doctor',
    'get_all_pharmacy_patients',
    'patient_info', 'update_patient','patient_medical_history', 'create_medical_record', 'update_primary_pharmacy',
    'add_user',
    'medication_info'
]

# Depreciated
def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        invalid_msg = {
            'message': 'Invalid token. Registration or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required',
            'authenticated': False
        }
        auth_headers = request.headers.get('Authorization', '').split()
        if len(auth_headers) != 2:
            return jsonify(invalid_msg), 401
        try:
            token = auth_headers[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user: User = User.query.filter_by(user_id=data['user_id']).first()
            if not user:
                raise RuntimeError('User not found')
            return f((user.user_id, user), *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401
        except (jwt.InvalidTokenError, Exception) as e:
            print(f'exception thrown message: {e}')
            return jsonify(invalid_msg), 401
    return _verify

# AUTHORIZATION EXCEPTION RESPONSES
class UnauthorizedError(JWTExtendedException):
    pass
def USER_NOT_AUTHORIZED(uid: int|None=None) -> Response:
    if uid:
        return jsonify({
            'error': f'User with id {uid} does not have permission to this resource'
        }), 401
    return jsonify({'error': 'User does not have permission to this resource'}), 401
