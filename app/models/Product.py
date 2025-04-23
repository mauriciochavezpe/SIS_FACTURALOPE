from app import db

from app.models.Auditoria import Auditoria
from .product_storage import product_storage

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    stock_inicial = db.Column(db.Integer, nullable=False)
    stock_actual = db.Column(db.Integer, nullable=False)
    estatus_id = db.Column(db.Integer, nullable=True)
    category_id = db.Column(db.Integer,nullable=False)
    
    # Relación muchos a muchos con Storage
    images = db.relationship(
        'Storage',
        secondary=product_storage,
        back_populates='products'
    )
    