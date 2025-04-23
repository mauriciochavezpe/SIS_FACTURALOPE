from app import db

from app.models.Auditoria import Auditoria

class MasterData(db.Model):
    id_document = db.Column(db.Integer, primary_key=True)
    type_document = db.Column(db.String(50), unique=True, nullable=False) # DNI, YAPE
    type_description = db.Column(db.String(255), nullable=False) # DOCUMENTO DE IDENTIDAD, YAPE
    is_active = db.Column(db.Boolean, default=True) 
    code_table = db.Column(db.String(50), nullable=False) #DOCUMENTOS_IDENTITY, METHODS_PAYMENT
    description_table = db.Column(db.String(255), nullable=False) # DOCUMENTO DE IDENTIDAD, PAGOS
    status  = db.Column(db.Integer, nullable=False)
    # is_client = db.Column(db.Boolean, default=False)