from flask import Blueprint,jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.product_service import get_all_products, create_product, update_product, delete_product
 #, create_user, update_user, delete_user, login_user
# from app.auth.jwt_handler import generate_jwt,decode_jwt
product_blueprint = Blueprint('products', __name__)

@product_blueprint.route('/', methods=['GET'])
def get_all_products_routes():
    products, status_code = get_all_products()
    return jsonify(products), status_code

@product_blueprint.route('/', methods=['POST'])
def create_product_routes():
    products, status_code = create_product()
    return jsonify(products), status_code    

@product_blueprint.route('/<int:id>', methods=['PUT'])
def update_product_routes(id):
    products, status_code = update_product(id)
    return jsonify(products), status_code    

@product_blueprint.route('/<int:id>', methods=['DELETE'])
def delete_product_routes(id):
    products, status_code = delete_product()
    return jsonify(products), status_code    
