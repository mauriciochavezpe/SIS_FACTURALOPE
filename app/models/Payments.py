from app import db

from app.models.Auditoria import Auditoria

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    method = db.Column(db.String(50), nullable=False)  # Tarjeta, efectivo, transferencia
    status = db.Column(db.String(50), nullable=False)  # Pendiente, completado, fallido
    
    