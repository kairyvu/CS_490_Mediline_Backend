from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from flaskr.services import get_medical_records_by_user, UnauthorizedError, USER_NOT_AUTHORIZED
from flasgger import swag_from

medical_record_bp = Blueprint('medical_record', __name__)

@medical_record_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@swag_from('../docs/medical_record_routes/get_medical_records.yml')
def get_medical_records(user_id):
    sort_by = request.args.get('sort_by')
    order = request.args.get('order')
    try:
        medical_records = get_medical_records_by_user(user_id=user_id, 
                                                      sort_by=sort_by, 
                                                      order=order, 
                                                      requesting_user=current_user)
        return jsonify(medical_records), 200
    except UnauthorizedError:
        return USER_NOT_AUTHORIZED(current_user.user_id)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the medical records'}), 500