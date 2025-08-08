
from flask_restx import Namespace, Resource, fields
from app.services.category_service import create_category, get_all_categories,update_category,delete_category

category_blueprint = Namespace('category', description='Category operations')

category_model = category_blueprint.model('CategoryModel', {
    'name': fields.String(required=True, description='The category name'),
    'description': fields.String(required=True, description='The category description'),
    'id_status': fields.Integer(required=True, description='The category status')
})

@category_blueprint.route('')
class CategoryList(Resource):
    def get(self):
        categories,status = get_all_categories()
        return categories,status

    @category_blueprint.expect(category_model)
    def post(self):
        category, status = create_category()
        return category, status

@category_blueprint.route('/<int:category_id>')
class Category(Resource):
    @category_blueprint.expect(category_model)
    def put(self, category_id):
        category,status = update_category(category_id)
        return category,status

    def delete(self, category_id):
        msg,status = delete_category(category_id)
        return msg, status