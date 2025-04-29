from flask import Blueprint, jsonify, send_file
from app.services.storage_service import (
    get_all_storage,
    create_storage,
    update_storage,
    delete_storage
)

storage_blueprint = Blueprint('storage', __name__)

@storage_blueprint.route('/', methods=['GET'])
def get_all_storage_routes():
    try:
        storage_items, status = get_all_storage()
        return jsonify({
            'status': 'success',
            'data': storage_items,
            'count': len(storage_items)
        }), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@storage_blueprint.route('/', methods=['POST'])
def create_storage_routes():
    try:
        storage, status = create_storage()
        return jsonify(storage), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@storage_blueprint.route('/<int:id>', methods=['PUT'])
def update_storage_routes(id):
    try:
        storage, status = update_storage(id)
        return jsonify(storage), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@storage_blueprint.route('/<int:id>', methods=['DELETE'])
def delete_storage_routes(id):
    try:
        result, status = delete_storage(id)
        return jsonify(result), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500