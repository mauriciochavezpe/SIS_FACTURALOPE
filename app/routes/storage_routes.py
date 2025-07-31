from flask_restx import Namespace, Resource, fields
from flask import send_file
from app.services.storage_service import (
    get_all_storage,
    create_storage,
    update_storage,
    delete_storage
)

storage_blueprint = Namespace('storage', description='Storage operations')

storage_model = storage_blueprint.model('StorageModel', {
    'file': fields.Raw(type='file', required=True, description='The file to upload')
})

@storage_blueprint.route('/')
class StorageList(Resource):
    def get(self):
        storage_items, status = get_all_storage()
        return storage_items, status

    @storage_blueprint.expect(storage_model)
    def post(self):
        storage, status = create_storage()
        return storage, status

@storage_blueprint.route('/<int:id>')
class Storage(Resource):
    @storage_blueprint.expect(storage_model)
    def put(self, id):
        storage, status = update_storage(id)
        return storage, status

    def delete(self, id):
        result, status = delete_storage(id)
        return result, status

@storage_blueprint.route('/download/<string:file_type>/<string:file_name>')
class StorageDownload(Resource):
    def get(self, file_type, file_name):
        try:
            file_path = f"app/{file_type}/{file_name}"
            return send_file(file_path, as_attachment=True)
        except FileNotFoundError:
            return {"error": "Archivo no encontrado"}, 404
        except Exception as e:
            return {"error": str(e)}, 500