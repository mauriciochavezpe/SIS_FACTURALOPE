from app.extension import db, bcrypt
from .Auditoria import Auditoria
from app.models.enums.document_types import DocumentType

class User(Auditoria):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    id_status = db.Column(db.Integer, nullable=True)
    document_number = db.Column(db.String(20), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def document_type_description(self):
        doc_type = DocumentType.get_by_code(self.document_type)
        return doc_type.description if doc_type else None

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'id_status': self.id_status,
            'document_number': self.document_number,
            'document_type': self.document_type_description
        }
