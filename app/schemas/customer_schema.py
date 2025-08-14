from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from app.models.entities.Customer import Customer
from marshmallow import fields

class CustomerSchema(SQLAlchemyAutoSchema):
    password_hash = fields.String(load_only=True)
    class Meta:
        model = Customer
        load_instance = True
        include_fk = True
    
    
