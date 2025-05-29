from flask import Blueprint, jsonify
from app.services.master_data_service import (
    get_all_master_data,
    create_master_data,
    update_master_data,
    delete_master_data,
    get_master_data_by_id,
    generacion_factura_dummy
)

master_data_blueprint = Blueprint('master_data', __name__)

@master_data_blueprint.route('/', methods=['GET'])
def get_all_master_data_routes():
    try:
        master_data, status = get_all_master_data()
        return jsonify(master_data), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@master_data_blueprint.route('/<int:id>', methods=['GET'])
def get_master_data_by_id_routes(id):
    try:
        master_data, status = get_master_data_by_id(id)
        return jsonify(master_data), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@master_data_blueprint.route('/', methods=['POST'])
def create_master_data_routes():
    try:
        master_data, status = create_master_data()
        return jsonify(master_data), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@master_data_blueprint.route('/<int:id>', methods=['PUT'])
def update_master_data_routes(id):
    try:
        master_data, status = update_master_data(id)
        return jsonify(master_data), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@master_data_blueprint.route('/<int:id>', methods=['DELETE'])
def delete_master_data_routes(id):
    try:
        result, status = delete_master_data(id)
        return jsonify(result), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@master_data_blueprint.route('/factura_dummy', methods=['GET','POST'])
def generacion_factura_dummy_routes():
    try:
        master_data, status = generacion_factura_dummy()
        return jsonify(master_data), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500
