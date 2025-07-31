from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields
from app.models.entities.Invoice import Invoice
from app.schemas.invoice_detail_schema import InvoiceDetailSchema

class InvoiceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Invoice
        load_instance = True
        include_fk = True

