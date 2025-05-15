from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.entities.InvoiceDetails import InvoiceDetail
from marshmallow import fields, validates, ValidationError

class InvoiceDetailNestedSchema(SQLAlchemyAutoSchema):
    discount = fields.Decimal(required=True)
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True)
    subtotal = fields.Decimal(required=True)
    tax = fields.Decimal(required=False)
    total = fields.Decimal(required=True)
    unit_price = fields.Decimal(required=True)

class ComplexInvoiceSchema(SQLAlchemyAutoSchema):
    product_id = fields.Integer(required=True)
    date = fields.DateTime(required=True)
    customer_id = fields.Integer(required=True)
    num_invoice = fields.String(required=True)
    subtotal = fields.Decimal(required=False)
    total = fields.Decimal(required=True)
    details = fields.List(fields.Nested(InvoiceDetailNestedSchema), required=True)

    @validates('details')
    def validate_details(self, details):
        if not details:
            raise ValidationError('Details cannot be empty')