from flask import Blueprint, request, jsonify
from flaskr.services import user_id_credentials
from flasgger import swag_from

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
@swag_from('../docs/auth_routes/login.yml')
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user_token = user_id_credentials(username, password)
    if user_token:
        return jsonify(user_token), 200
    return jsonify({
            "error": "Invalid credentials",
            "authenticated": False
        }), 401