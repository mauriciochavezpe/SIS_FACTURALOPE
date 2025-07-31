from flask_restx import Namespace, Resource, fields
from app.services.master_data_service import (
    get_all_master_data,
    create_master_data,
    update_master_data,
    delete_master_data,
    get_master_data_by_id,
    generacion_factura_dummy
)

master_data_blueprint = Namespace('master_data', description='Master data operations')

master_data_model = master_data_blueprint.model('MasterDataModel', {
    'catalog_code': fields.String(required=True, description='The catalog code'),
    'code': fields.String(required=True, description='The code'),
    'value': fields.String(required=True, description='The value'),
    'description': fields.String(description='The description'),
    'is_active': fields.Boolean(description='Is active?'),
    'status_id': fields.Integer(description='The status ID'),
    'extra': fields.String(description='Extra field'),
    'extra2': fields.String(description='Extra field 2'),
    'extra3': fields.String(description='Extra field 3')
})

@master_data_blueprint.route('/')
class MasterDataList(Resource):
    def get(self):
        master_data, status = get_all_master_data()
        return master_data, status

    @master_data_blueprint.expect(master_data_model)
    def post(self):
        master_data, status = create_master_data()
        return master_data, status

@master_data_blueprint.route('/<int:id>')
class MasterData(Resource):
    def get(self, id):
        master_data, status = get_master_data_by_id(id)
        return master_data, status

    @master_data_blueprint.expect(master_data_model)
    def put(self, id):
        master_data, status = update_master_data(id)
        return master_data, status

    def delete(self, id):
        result, status = delete_master_data(id)
        return result, status

@master_data_blueprint.route('/factura_dummy')
class MasterDataDummy(Resource):
    def get(self):
        master_data, status = generacion_factura_dummy()
        return master_data, status
    def post(self):
        master_data, status = generacion_factura_dummy()
        return master_data, status
