from celery.result import AsyncResult
from flask import Blueprint, jsonify, request, Response
from flaskr.services import get_all_pharmacy_patients
from flaskr.services.pharmacy_service import add_together
from flasgger import swag_from


pharmacy_bp = Blueprint('pharmacy', __name__)
@pharmacy_bp.route('/<int:pharmacy_id>/patients', methods=['GET'])
@swag_from('../docs/pharmacy_routes/get_pharmacy_patients.yml')
def get_pharmacy_patients(pharmacy_id):
    try:
        history = get_all_pharmacy_patients(pharmacy_id=pharmacy_id)
        return jsonify(history), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the medications history'}), 500



@pharmacy_bp.route('/add', methods=['POST'])
def start_add():
    """Code snippet from [here](https://flask.palletsprojects.com/en/stable/patterns/celery/#calling-tasks)"""
    a = request.json.get('a')
    b = request.json.get('b')
    res = add_together.delay(a, b)
    return jsonify({'result_id': res.id})

@pharmacy_bp.route('/result/<id>', methods=['GET'])
def task_result(id: str):
    res = AsyncResult(id)
    return jsonify({
        'ready': res.ready(),
        'successful': res.successful(),
        'value': res.result if res.ready() else None
    })