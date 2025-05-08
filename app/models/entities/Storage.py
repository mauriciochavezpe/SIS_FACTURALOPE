from app import db

from .Auditoria import Auditoria
from app.models.associations.product_storage import product_storage
class Storage(Auditoria): #almacenamineto de los archivos
    id = db.Column(db.Integer, primary_key=True)
    string_path = db.Column(db.String(500), nullable=True)
    match_id = db.Column(db.Integer, nullable=True)
    eid_status = db.Column(db.Integer, default=False)
    category_id = db.Column(db.Integer, nullable=True)
    file_path = db.Column(db.String(500), nullable=False)  # Ruta al archivo
    file_name = db.Column(db.String(255), nullable=False)  # Nombre del archivo
    file_type = db.Column(db.String(50), nullable=False)   # Tipo de archivo (image, document, etc.)
    file_size = db.Column(db.Integer, nullable=True)       # Tamaño del archivo en bytes
    
       # Relación inversa con Product
    products = db.relationship(
        'Product',
        secondary=product_storage,
        back_populates='images'
    )