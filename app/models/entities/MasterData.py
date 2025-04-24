from app import db

from app.models.Auditoria import Auditoria
class MasterData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_value = db.Column(db.String(50), unique=True, nullable=False) # DNI, YAPE  | lacteos
    description_value = db.Column(db.String(255), nullable=False) # DOCUMENTO DE IDENTIDAD, YAPE | lacteos
    is_active = db.Column(db.Boolean, default=True) 
    code_table = db.Column(db.String(50), nullable=False) #DOCUMENTOS_IDENTITY, METHODS_PAYMENT | categoria de productos | 
    description_table = db.Column(db.String(255), nullable=False) # DOCUMENTO DE IDENTIDAD, PAGOS | categoria de lacteos |
    id_status  = db.Column(db.Integer, nullable=False)
    # is_client = db.Column(db.Boolean, default=False)
    
    # Relationship
    # user_type = db.relationship(
    #     'User',
    #     secondary=user_typedocument,
    #     back_populates='master_data'
    # )
    
    
    # products = db.relationship("Product", back_populates="category")  # 👈 uno a muchos