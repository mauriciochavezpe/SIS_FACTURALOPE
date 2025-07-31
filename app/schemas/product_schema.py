from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from app import db
from app.models.entities.Product import Product
from .category_schema import CategorySchema

class ProductSchema(SQLAlchemyAutoSchema):
    category = Nested(CategorySchema)
    class Meta:
        model = Product
        load_instance = True
        include_fk = True
        exclude = ('invoice_details',)
        
