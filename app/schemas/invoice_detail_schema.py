from marshmallow_sqlalchemy import SQLAlchemyAutoSchema,fields
from app.models.entities.InvoiceDetails import InvoiceDetail
from app.schemas.product_schema import ProductSchema

class InvoiceDetailSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = InvoiceDetail
        load_instance = True
        include_fk = True
    
    product = fields.Nested(ProductSchema)  
    
    # id = auto_field()
    # invoice_id = auto_field()
    # product_id = auto_field()
    # quantity = auto_field()
    # unit_price = auto_field()
    # discount = auto_field()
    # subtotal = auto_field()
    # tax = auto_field()
    # total = auto_field()