from flask import Blueprint, jsonify
from flaskr.services import get_user_info_by_id
from flasgger import swag_from
from flaskr.extensions import db

user_bp = Blueprint('user_bp', __name__)
@user_bp.route('/<int:user_id>', methods=['GET'])
@swag_from('../docs/user_routes/get_user_by_id.yml')

def get_user_by_id(user_id):
    try:
        user_info = get_user_info_by_id(user_id)
        return jsonify(user_info), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500