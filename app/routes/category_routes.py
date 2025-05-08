
from flask import Blueprint, jsonify, request
from app.services.category_service import create_category, get_all_categories,update_category,delete_category
category_blueprint = Blueprint('category', __name__)

@category_blueprint.route('/', methods=['POST'])
def create_category_route():
    try:
        category_data = request.get_json()
        category, status = create_category(category_data)
        return jsonify(category), status
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@category_blueprint.route('/', methods=['GET'])
def get_all_categories_route():
    try:
        categories,status = get_all_categories()
        return jsonify(categories),status
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@category_blueprint.route('/<int:category_id>', methods=['PUT'])
def update_category_route(category_id):
    try:
        category_data = request.get_json()
        category,status = update_category(category_id,category_data)
        return jsonify(category),status
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@category_blueprint.route('/<int:category_id>', methods=['DELETE'])
def delete_category_route(category_id):
    try:
        status = delete_category(category_id)
        return jsonify({'message': 'Category deleted successfully'}), status
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500