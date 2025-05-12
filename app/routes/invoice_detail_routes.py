from flask import Blueprint, jsonify
from app.services.invoice_detail_service import (
    get_invoice_details_all,
    create_invoice_detail,
    update_invoice_detail,
    delete_invoice_detail
)

invoice_detail_blueprint = Blueprint('invoice_details', __name__)

@invoice_detail_blueprint.route('/', methods=['GET'])
# @invoice_detail_blueprint.route('/invoice/<int:invoice_id>', methods=['GET'])
def get_details_routes():
    try:
        details, status = get_invoice_details_all()
        return jsonify({
            'status': 'success',
            'data': details,
            'count': len(details)
        }), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoice_detail_blueprint.route('/invoice/<int:invoice_id>', methods=['GET'])
def get_details_by_invoice(invoice_id):
    try:
        details, status = get_invoice_details_all(invoice_id)
        return jsonify({
            'status': 'success',
            'data': details,
            'count': len(details)
        }), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@invoice_detail_blueprint.route('/', methods=['POST'])
def create_detail_routes():
    try:
        detail, status = create_invoice_detail()
        return jsonify(detail), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoice_detail_blueprint.route('/<int:id>', methods=['PUT'])
def update_detail_routes(id):
    try:
        detail, status = update_invoice_detail(id)
        return jsonify(detail), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoice_detail_blueprint.route('/<int:id>', methods=['DELETE'])
def delete_detail_routes(id):
    try:
        result, status = delete_invoice_detail(id)
        return jsonify(result), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500