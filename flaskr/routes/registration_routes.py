"""\
    Route for user registration in Mediline API Backend
"""
from werkzeug.datastructures import ImmutableMultiDict
from flask import Blueprint, request, make_response, jsonify
from flaskr.services import add_user
from flasgger import swag_from

from sqlalchemy.exc import IntegrityError

register_bp = Blueprint("register", __name__)

@register_bp.route('/', methods=['POST'])
@swag_from('../docs/registration_routes/register.yml')
def register():
    content_type = request.content_type.split(';')[0]
    form_data: ImmutableMultiDict|None = None
    if content_type != 'application/json':
        return make_response(jsonify({'error': f'bad content type: {content_type}'}), 415)
    form_json = request.get_json()
    try:
        # Cast json data from request to werkzeug ImmutableMultiDict
        # This is done to be compatible with add_user
        form_data = ImmutableMultiDict(list(dict(form_json).items()))
    except Exception as e:
        return make_response(jsonify({
            'error': 'form data is not valid',
            'details': str(e)
        }), 400)
    try:
        return add_user(form_data)
    except IntegrityError as e:
        #error_msg = str((str(e.args[0]).split(maxsplit=1))[1]).split(',')[1].strip().strip(')"\\')
        error_msg = str(e)
        return make_response(jsonify({'error': f'{error_msg}'}), 400)