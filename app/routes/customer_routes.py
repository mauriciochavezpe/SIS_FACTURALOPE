from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.customer_service import (get_all_customers,
create_customer, get_customers_by_id, update_customers_by_id)
# from app.auth.jwt_handler import generate_jwt,decode_jwt
customer_blueprint = Blueprint('customers', __name__)
@customer_blueprint.route('/', methods=['GET'])
def get_all_customers_routes():
    try:
        customers,status = get_all_customers()
        return jsonify(customers), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_blueprint.route('/', methods=['POST'])
def create_user_routes():
    try:
        customers,status = create_customer()
        return jsonify(customers), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#obteener un usuario por id
@customer_blueprint.route('/<int:user_id>', methods=['GET'])
def get_user_by_id_routes(user_id):
    try:
        users,status = get_customers_by_id(user_id)
        return users, status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_blueprint.route('/<int:user_id>', methods=['PUT'])
def update_user_routes(user_id):
    try:
        users,status = update_customers_by_id(user_id)
        return jsonify(users), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500
'''


@customer_blueprint.route('/login', methods=['POST'])
def login_user_routes():
    try:
        users,status = login_user()
        return jsonify(users), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_blueprint.route('/logout', methods=['POST'])        
def logout_user_routes():
    try:
        users,status = logout_user()
        return jsonify(users), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500
'''
