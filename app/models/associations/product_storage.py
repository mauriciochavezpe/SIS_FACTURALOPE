from app import db

product_storage = db.Table(
    'product_storage',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('storage_id', db.Integer, db.ForeignKey('storage.id'), primary_key=True)
)
