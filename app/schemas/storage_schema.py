from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from app import db

from app.models.Storage import Storage

class StorageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Storage
        load_instance = True
        include_fk = True
        