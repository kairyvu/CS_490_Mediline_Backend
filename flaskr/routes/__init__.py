from flask import Blueprint, Flask
from .database import database_bp
from .exercise_routes import exercise_bp
from .payment_routes import payment_bp
from .appointment_routes import appointment_bp
from .report_routes import report_bp
from .prescription_routes import prescription_bp
from .chat_routes import chat_bp

main_bp = Blueprint('main', __name__)

def register_routes(app: Flask):
    app.register_blueprint(database_bp, url_prefix='/test_connection')
    app.register_blueprint(exercise_bp, url_prefix='/exercise')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(appointment_bp, url_prefix='/appointment')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(prescription_bp, url_prefix='/prescription')
    app.register_blueprint(chat_bp, url_prefix='/chat')