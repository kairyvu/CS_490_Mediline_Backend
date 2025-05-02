from flask import Blueprint, Flask, Response, jsonify
from .database import database_bp
from .registration_routes import register_bp
from .exercise_routes import exercise_bp
from .payment_routes import payment_bp
from .appointment_routes import appointment_bp
from .report_routes import report_bp
from .prescription_routes import prescription_bp
from .chat_routes import chat_bp
from .social_media_routes import social_media_bp
from .auth_routes import auth_bp
from .patient_routes import patient_bp
from .doctor_routes import doctor_bp
from .pharmacy_routes import pharmacy_bp
from .medication_routes import medication_bp
from .user_routes import user_bp


main_bp = Blueprint('main', __name__)

def register_routes(app: Flask):
    app.register_blueprint(database_bp, url_prefix='/test_connection')
    app.register_blueprint(exercise_bp, url_prefix='/exercise')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(appointment_bp, url_prefix='/appointment')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(prescription_bp, url_prefix='/prescription')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(social_media_bp, url_prefix='/social_media')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(register_bp, url_prefix='/register')
    app.register_blueprint(pharmacy_bp, url_prefix='/pharmacy')
    app.register_blueprint(medication_bp, url_prefix='/medication')
    app.register_blueprint(user_bp, url_prefix='/user')
