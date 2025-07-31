from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
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
    date = fields.DateTime(required=True)
    customer_id = fields.Integer(required=True)
    num_invoice = fields.String(required=False)
    subtotal = fields.Decimal(required=False)
    serie = fields.String(required=False)
    tax = fields.Decimal(required=False)
    document_type = fields.Integer(required=False)
    related_invoice_id = fields.Integer(required=False)
    total = fields.Decimal(required=True)
    details = fields.List(fields.Nested(InvoiceDetailNestedSchema), required=True)

    @validates('details')
    def validate_details(self, details):
        if not details:
            raise ValidationError('Details cannot be empty')

class InvoiceWithDetailsSchema(SQLAlchemyAutoSchema):
    invoice_details = fields.List(fields.Nested(InvoiceDetailNestedSchema))

    class Meta:
        # Provide the model class for SQLAlchemyAutoSchema
        from app.models.entities.Invoice import Invoice
        model = Invoice
        load_instance = True
        include_fk = True
