from flask import Blueprint,jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import get_all_users #, create_user, update_user, delete_user, login_user
# from app.auth.jwt_handler import generate_jwt,decode_jwt
user_blueprint = Blueprint('users', __name__)

@user_blueprint.route('/', methods=['GET'])
def get_all_users_routes():
    try:
        users = get_all_users()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500