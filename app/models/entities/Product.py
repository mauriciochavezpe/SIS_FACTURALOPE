from app import db

from .Auditoria import Auditoria
from app.models.associations.product_storage import product_storage
from .Category import Category

class Product(Auditoria):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    stock_inicial = db.Column(db.Integer, nullable=False) # stock semanal
    stock_actual = db.Column(db.Integer, nullable=False) # stock diario  
    id_status = db.Column(db.Integer, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    
    # Relación muchos a muchos con Storage
    images = db.relationship(
        'Storage',
        secondary=product_storage,
        back_populates='products'
    )
    
    invoice_details = db.relationship('InvoiceDetail', back_populates='product')
    
    category = db.relationship("Category", uselist=False, back_populates="products")
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'stock_inicial': self.stock_inicial,
            'stock_actual': self.stock_actual,
            'status': self.status.value if self.status else None,
            'category': self.category.value if self.category else None,
            'images': [img.file_path for img in self.images]
        }