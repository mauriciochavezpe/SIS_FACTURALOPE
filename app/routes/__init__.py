from app.routes.user_routes import user_blueprint
from app.routes.product_routes import product_blueprint


def register_blueprints(app):     
    app.register_blueprint(user_blueprint, url_prefix='/api/users')
    app.register_blueprint(product_blueprint, url_prefix='/api/products')