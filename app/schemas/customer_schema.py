from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.Customer import Customer

class CustomerSchema(SQLAlchemySchema):
    class Meta:
        model = Customer
        load_instance = True
        include_fk = True
    
    id = auto_field()
    business_name = auto_field()
    commercial_name = auto_field()
    document_type_id = auto_field()
    document_number = auto_field()
    email = auto_field()
    phone = auto_field()
    mobile = auto_field()
    address = auto_field()
    district = auto_field()
    city = auto_field()
    country = auto_field()
    is_active = auto_field()
    credit_limit = auto_field()
    payment_term_days = auto_field()