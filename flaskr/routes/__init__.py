from flask import Blueprint, Flask
from .database import database_bp
from .exercise_routes import exercise_bp
from .payment_routes import payment_bp

main_bp = Blueprint('main', __name__)

def register_routes(app: Flask):
    app.register_blueprint(database_bp, url_prefix='/test_connection')
    app.register_blueprint(exercise_bp, url_prefix='/exercise')
    app.register_blueprint(payment_bp, url_prefix='/payment')