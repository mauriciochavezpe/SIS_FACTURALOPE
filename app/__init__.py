from flask import Flask
from app.config.config import Config
from app.extension import db, migrate, jwt
from app.routes import register_blueprints
# from app.swagger import api
# from flasgger import Swagger
# migrate =Migrate()
 # invocamos al servicio batch
# from app.utils.Storage.config import authenticate_service_account
 
 
def create_app(text='testing'):
        app = Flask(__name__) 
        app.config.from_object(Config)
        # Inicializar extensiones
        db.init_app(app)
        migrate.init_app(app, db)  # Integrar Flask-Migrate con la app y SQLAlchemy
        jwt.init_app(app)  # Integrar Flask-Migrate con la app y SQLAlchemy
        register_blueprints(app)
        # Swagger
        # api.init_app(app)
        # from app.models import   # ajusta según tus modelos
        from app.models import User,Customer,MasterData, Invoice, InvoiceDetail, Product, Payment
        # drive_service = authenticate_service_account()
        # print("Autenticación exitosa, {drive_service}")
        
        return app

 