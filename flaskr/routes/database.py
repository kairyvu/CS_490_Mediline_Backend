from flask import Blueprint
from flaskr.services import get_tables

database_bp = Blueprint("database", __name__)

@database_bp.route('/', methods=['GET'])
def fetch_tables():
    return get_tables()
