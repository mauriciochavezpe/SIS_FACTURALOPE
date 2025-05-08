from app import db

from .Auditoria import Auditoria
from app.models.enums.document_types import DocumentType
# from .associations.user_typedocument import user_typedocument
class User(Auditoria):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False) #true si es admin, false si es cliente
    id_status = db.Column(db.Integer, nullable=False)
    document_number = db.Column(db.String(20), unique=True, nullable=False)

    # Relationship with MasterData
    # master_data = db.relationship(
    #     'MasterData',
    #     secondary=user_typedocument,
    #     back_populates='user_type'
    # )
    
    # POR DEFECTO TRAERA 1 - DNI
    @property
    def document_type_description(self):
        doc_type = DocumentType.get_by_code(self.document_type)
        return doc_type.description if doc_type else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'id_status': self.id_status,
            'document_number': self.document_number,
            'document_type': self.document_type_description
        }