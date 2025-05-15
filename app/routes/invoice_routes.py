from flask import Blueprint, jsonify
from app.services.invoice_service import (
    get_all_invoices,
    create_invoice,
    update_invoice,
    delete_invoice,
    get_details_by_invoice,
    create_invoice_details
)

invoice_blueprint = Blueprint('invoices', __name__)

@invoice_blueprint.route('/', methods=['GET'])
def get_all_invoices_routes():
    try:
        invoices, status = get_all_invoices()
        return jsonify({
            'status': 'success',
            'data': invoices,
            'count': len(invoices)
        }), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoice_blueprint.route('/', methods=['POST'])
def create_invoice_routes():
    try:
        invoice, status = create_invoice()
        return jsonify(invoice), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoice_blueprint.route('/<int:id>', methods=['PUT'])
def update_invoice_routes(id):
    try:
        invoice, status = update_invoice(id)
        return jsonify(invoice), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoice_blueprint.route('/<int:id>', methods=['DELETE'])
def delete_invoice_routes(id):
    try:
        result, status = delete_invoice(id)
        return jsonify(result), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@invoice_blueprint.route('/details/<int:id>', methods=['GET'])
def get_details_by_invoice_routes(id):
    try:
        invoice, status = get_details_by_invoice(id)
        return jsonify(invoice), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@invoice_blueprint.route('/details', methods=['POST'])
def create_invoice_details_routes():
    try:
        invoice_details, status = create_invoice_details()
        return jsonify(invoice_details), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500
