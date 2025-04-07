from flask import Blueprint, request, jsonify
from flaskr.services import auth_service

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user_info = auth_service.user_id_credentials(username, password)
    if user_info:
        return jsonify(user_info), 200
    return jsonify({"error": "Invalid credentials"}), 401


