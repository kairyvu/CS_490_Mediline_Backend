from flask import Blueprint, jsonify, request
from flaskr.services import get_invoices_by_user
from flasgger import swag_from

payment_bp = Blueprint("payment", __name__)

@payment_bp.route('/user/<int:user_id>', methods=['GET'])
@swag_from('../docs/payment_routes/get_invoices_by_user_route.yml')
def get_invoices_by_user_route(user_id):
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    
    try:
        invoices = get_invoices_by_user(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(invoices), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400