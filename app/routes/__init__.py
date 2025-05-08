from app.routes import (user_routes, product_routes, category_routes,
                        invoice_routes,invoice_detail_routes,
                        customer_routes,storage_routes, master_data_routes,invoice_routes)
# from app.routes.product_routes import product_blueprint


def register_blueprints(app):     
    app.register_blueprint(user_routes.user_blueprint, url_prefix='/api/users')
    app.register_blueprint(product_routes.product_blueprint, url_prefix='/api/products')
    app.register_blueprint(category_routes.category_blueprint, url_prefix='/api/categories')
    app.register_blueprint(storage_routes.storage_blueprint, url_prefix='/api/storages')
    app.register_blueprint(customer_routes.customer_blueprint, url_prefix='/api/customers')
    app.register_blueprint(master_data_routes.master_data_blueprint, url_prefix='/api/master_data')
    app.register_blueprint(invoice_routes.invoice_blueprint, url_prefix='/api/invoices')
    app.register_blueprint(invoice_detail_routes.invoice_detail_blueprint, url_prefix='/api/invoices_details')