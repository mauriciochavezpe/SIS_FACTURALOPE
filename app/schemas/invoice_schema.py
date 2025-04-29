from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.entities.Invoice import Invoice

class InvoiceSchema(SQLAlchemySchema):
    class Meta:
        model = Invoice
        load_instance = True
        include_fk = True
    
    id = auto_field()
    invoice_number = auto_field()
    customer_id = auto_field()
    date = auto_field()
    due_date = auto_field()
    total = auto_field()
    status_id = auto_field()
    created_at = auto_field()
    updated_at = auto_field()