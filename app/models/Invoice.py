from app import db

from app.models.Auditoria import Auditoria

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False) # ruc, boleta
    type_invoice_id = db.Column(db.Integer, nullable=False)  # Factura, nota de crédito, nota de débito
    date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    total = db.Column(db.Float, nullable=False)
    num_invoice = db.Column(db.String(50), unique=True, nullable=False) #F001-0001, B001-0001

    invoice_details = db.relationship('InvoiceDetail', back_populates='invoice')