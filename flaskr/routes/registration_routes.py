"""\
    Route for user registration in Mediline API Backend
    - accepts only http POST requests with content types of:
      - application/json
      - application/x-www-form-urlencoded
      - multipart/form-data
      then makes it into a werkzeug ImmutableMultiDict
"""
from werkzeug.datastructures import ImmutableMultiDict
from flask import Blueprint, request, make_response, jsonify
from flaskr.services.registration_service import add_user

from sqlalchemy.exc import IntegrityError

register_bp = Blueprint("register", __name__)

@register_bp.route('/', methods=['POST'])
def register():
    # Check data not empty
    if not request.get_data():
        return make_response(jsonify(message=f'no data provided'), 400)
    # Coerce json data from request to match http form data in werkzeug
    # This is done to be compatible with add_user
    content_type = request.content_type.split(';')[0]
    form_data: ImmutableMultiDict|None = None
    match content_type:
        case 'application/json':
            form_data = ImmutableMultiDict(list(dict(request.get_json()).items()))
        case 'multipart/form-data'|'application/x-www-form-urlencoded':
            form_data = request.form
        case _:
            return make_response(jsonify(message=f'bad content type: {content_type}'), 400)
    try:
        return add_user(form_data)
    except IntegrityError as e:
        return make_response(jsonify(
            {
                'error': f'inserting duplicate user with data: {form_data.to_dict()}'
            }
        ))