from app import db
from .Auditoria import Auditoria

class MasterData(Auditoria):
    id = db.Column(db.Integer, primary_key=True)
    catalog_code = db.Column(db.String(50), nullable=True)      # Ej: 'T_ESTADO', 'T_SUNAT', 'T_CATEGORIA'
    code = db.Column(db.String(50), nullable=True)              # Ej: 'IGV', '01', 'CAT01'
    value = db.Column(db.String(255), nullable=True)             # Ej: '0.18', 'LÁCTEOS'
    description = db.Column(db.String(255), nullable=True)       # Ej: 'Impuesto General a las Ventas', 'Lácteos'
    is_active = db.Column(db.Boolean, default=True)
    status_id = db.Column(db.Integer, nullable=True)
    extra = db.Column(db.String(255), nullable=True)  
    extra2 = db.Column(db.String(255), nullable=True)
    extra3 = db.Column(db.String(255), nullable=True)
    
    invoices = db.relationship('Invoice', back_populates='status', lazy=True)
    # __table_args__ = (
    #     db.UniqueConstraint('catalog_code', 'value', name='uq_catalog_code_code'),
    # )
    
    