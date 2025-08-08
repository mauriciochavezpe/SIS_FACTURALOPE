from flask_restx import Namespace, Resource, fields
from app.services.product_service import get_all_products, create_product, update_product, delete_product

product_blueprint = Namespace('products', description='Product operations')

product_model = product_blueprint.model('ProductModel', {
    'name': fields.String(required=True, description='The product name'),
    'price': fields.Float(required=True, description='The product price'),
    'description': fields.String(description='The product description'),
    'stock_inicial': fields.Integer(required=True, description='The initial stock'),
    'stock_actual': fields.Integer(required=True, description='The current stock'),
    'id_status': fields.Integer(description='The product status'),
    'category_id': fields.Integer(description='The category ID')
})

@product_blueprint.route('')
class ProductList(Resource):
    def get(self):
        products, status_code = get_all_products()
        return products, status_code

    @product_blueprint.expect(product_model)
    def post(self):
        products, status_code = create_product()
        return products, status_code

@product_blueprint.route('/<int:id>')
class Product(Resource):
    @product_blueprint.expect(product_model)
    def put(self, id):
        products, status_code = update_product(id)
        return products, status_code

    def delete(self, id):
        products, status_code = delete_product(id)
        return products, status_code    
