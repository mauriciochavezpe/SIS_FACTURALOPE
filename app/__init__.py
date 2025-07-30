from flask import Flask
from app.config.config import Config
from app.extension import db, migrate, bcrypt
from app.routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    # jwt.init_app(app)
    
    register_blueprints(app)
    
    # Importar modelos para que Alembic los detecte
    from app.models.entities import User, Customer, MasterData, Invoice, InvoiceDetails, Product, Payments, Serie

    return app