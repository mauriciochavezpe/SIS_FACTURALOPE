from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from app.models.entities.Customer import Customer

class CustomerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        include_fk = True
    
    # id = auto_field()
    # business_name = auto_field()
    # commercial_name = auto_field()
    # document_type = auto_field()
    # document_number = auto_field()
    # email = auto_field()
    # phone = auto_field()
    # username = auto_field()
    # is_active = auto_field()
    # is_business = auto_field()
    # address = auto_field()
    # city = auto_field()
    # country = auto_field()