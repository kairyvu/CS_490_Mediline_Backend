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
from flaskr.services.register import add_user

register_bp = Blueprint("register", __name__)

@register_bp.route('/', methods=['POST'])
def register_route():
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
    return add_user(form_data)