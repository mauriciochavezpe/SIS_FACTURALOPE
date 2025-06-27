from app import db

from .Auditoria import Auditoria
class Serie(Auditoria):
    id = db.Column(db.Integer, primary_key=True)
    tipo_comprobante = db.Column(db.String(2), nullable=False)  # '01'=Factura, '03'=Boleta, '07'=Nota Crédito, '08'=Nota Débito
    serie = db.Column(db.String(10), nullable=False)  # Ejemplo: 'F001'
    ultimo_correlativo = db.Column(db.Integer, nullable=False, default=0)
    
    __table_args__ = (db.UniqueConstraint('tipo_comprobante', 'serie', name='uq_tipo_serie'),)
