from app import db

from .Auditoria import Auditoria

class Invoice(Auditoria):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False) # ruc, boleta
    # type_invoice_id = db.Column(db.Integer, nullable=False)  # Factura, nota de crédito, nota de débito
    num_invoice = db.Column(db.String(50), unique=True, nullable=False) #F001-0001, B001-0001
    date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    due_date = db.Column(db.DateTime, nullable=True)
    total = db.Column(db.Numeric(12,2), nullable=False, default=0) # total de la factura
    subtotal = db.Column(db.Numeric(12,2), nullable=False, default=0)
    tax = db.Column(db.Numeric(12,2), nullable=False, default=0) # IGV
    id_status = db.Column(db.Integer, db.ForeignKey('master_data.id'), nullable=False)
    serie = db.Column(db.String(10), nullable=True) # F001, B001

    invoice_details = db.relationship('InvoiceDetail', back_populates='invoice', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Invoice {self.num_invoice}>'