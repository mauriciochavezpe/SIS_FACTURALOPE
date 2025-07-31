from app.swagger import api
from app.routes.user_routes import user_blueprint
from app.routes.product_routes import product_blueprint
from app.routes.category_routes import category_blueprint
from app.routes.storage_routes import storage_blueprint
from app.routes.customer_routes import customer_blueprint
from app.routes.master_data_routes import master_data_blueprint
from app.routes.invoice_routes import invoice_blueprint
from app.routes.invoice_detail_routes import invoice_detail_blueprint

api.add_namespace(user_blueprint, path='/api/users')
api.add_namespace(product_blueprint, path='/api/products')
api.add_namespace(category_blueprint, path='/api/categories')
api.add_namespace(storage_blueprint, path='/api/storages')
api.add_namespace(customer_blueprint, path='/api/customers')
api.add_namespace(master_data_blueprint, path='/api/master_data')
api.add_namespace(invoice_blueprint, path='/api/invoices')
api.add_namespace(invoice_detail_blueprint, path='/api/invoices_details')