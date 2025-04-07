from flask import Blueprint, request, jsonify
from flaskr.models import User, Patient, Doctor, Pharmacy
from flaskr.services.register import add_user

register_bp = Blueprint("register", __name__)

@register_bp.route('/', methods=['GET', 'POST'])
def register_route():
    if request.method == 'GET':
        return "IN register.get"
    elif request.method == 'POST':
        return add_user(request.get_json())
