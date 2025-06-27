from app import db
from .Auditoria import Auditoria

from decimal import Decimal

class InvoiceDetail(Auditoria):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12,2), nullable=False)
    discount = db.Column(db.Numeric(12,2), default=0)
    subtotal = db.Column(db.Numeric(12,2), nullable=False)
    tax = db.Column(db.Numeric(12,2), nullable=False)  # IGV por línea
    total = db.Column(db.Numeric(12,2), nullable=False) # Total precio
    
    # invoice = db.relationship('Invoice', back_populates='invoice_details')
     # Relación con Product
    product = db.relationship(
        'Product',
        back_populates='invoice_details',
        lazy='joined'
    )
    
    invoice = db.relationship(
        'Invoice',
        back_populates='invoice_details',
        lazy='joined'
    )
    
    def __repr__(self):
        return f'<InvoiceDetail {self.id} - Invoice {self.invoice_id}>'
    
    def calculate_totals(self):
        """Calcula los totales del detalle"""
        self.subtotal = Decimal(self.quantity) * Decimal(self.unit_price)
        if self.discount:
            self.subtotal -= Decimal(self.discount)
        self.tax = self.subtotal * Decimal('0.18')  # IGV 18%
        self.total = self.subtotal + self.tax