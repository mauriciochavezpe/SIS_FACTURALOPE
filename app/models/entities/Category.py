from app import db

from app.models.entities.Auditoria import Auditoria

class Category(Auditoria):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(120), unique=True, nullable=False)
    id_status = db.Column(db.Integer, default=False)
   
   
   
    products = db.relationship("Product", back_populates="category")  # 👈 uno a muchos
   