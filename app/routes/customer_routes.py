from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import get_all_users, create_user,update_user,get_user_by_id,login_user,logout_user #  , update_user, delete_user, login_user
# from app.auth.jwt_handler import generate_jwt,decode_jwt
customer_blueprint = Blueprint('customers', __name__)

@customer_blueprint.route('/', methods=['GET'])
def get_all_users_routes():
    try:
        users,status = get_all_users()
        return jsonify(users), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_blueprint.route('/', methods=['POST'])
def create_user_routes():
    try:
        users,status = create_user()
        return jsonify(users), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#obteener un usuario por id
@customer_blueprint.route('/<int:user_id>', methods=['GET'])
def get_user_by_id_routes(user_id):
    try:
        users,status = get_user_by_id(user_id)
        return users, status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_blueprint.route('/<int:user_id>', methods=['PUT'])
def update_user_routes(user_id):
    try:
        users,status = update_user(user_id)
        return jsonify(users), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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