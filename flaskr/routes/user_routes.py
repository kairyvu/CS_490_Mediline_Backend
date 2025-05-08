from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, current_user
from flask_jwt_extended.exceptions import NoAuthorizationError
from flaskr.services import get_user_info_by_id, UnauthorizedError, USER_NOT_AUTHORIZED
from flasgger import swag_from
from flaskr.extensions import db

user_bp = Blueprint('user_bp', __name__)
@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@swag_from('../docs/user_routes/get_user_info_by_id.yml')
def get_user_by_id(user_id):
    try:
        user_info = get_user_info_by_id(user_id, requesting_user=current_user)
        return jsonify(user_info), 200
    except NoAuthorizationError:
        return jsonify({"error": "You must be logged in to do this"}), 401
    except UnauthorizedError:
        return USER_NOT_AUTHORIZED(current_user.user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500