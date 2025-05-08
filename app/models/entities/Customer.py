from app import db

from .Auditoria import Auditoria
from app.models.enums.document_types import DocumentType # TIPO DOCUMENTO según SUNAT

class Customer(Auditoria):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    document_number = db.Column(db.String(21), unique=True, nullable=False)

    is_active = db.Column(db.Boolean, default=True)
    
    is_business = db.Column(db.Boolean, default=False)
    commercial_name = db.Column(db.String(100), nullable=True) # Nombre comercial
    business_name = db.Column(db.String(100), nullable=False)  # Razón social o nombre
    address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    province = db.Column(db.String(50), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(50), nullable=True)

    document_type = db.Column(
        db.String(1), 
        nullable=False, 
        default=DocumentType.DNI.code,
        comment='Tipo de documento según SUNAT'
    )
    invoices = db.relationship('Invoice', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.business_name}>'
    
    @property
    def document_type_description(self):
        doc_type = DocumentType.get_by_code(self.document_type)
        return doc_type.description if doc_type else None