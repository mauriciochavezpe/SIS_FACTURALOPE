from flask import Flask
from app.config.config import Config
from app.extension import db, migrate, bcrypt
from app.swagger import api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    # jwt.init_app(app)
    
    # Initialize Swagger
    api.init_app(app)

    # Import routes
    from app import routes
    
    # Import models for Alembic detection
    from app.models.entities import User, Customer, MasterData, Invoice, InvoiceDetails, Product, Payments, Serie

    return app