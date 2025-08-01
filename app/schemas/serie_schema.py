from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from app import db
from app.models.entities.Serie import Serie

class SerieSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Serie
        load_instance = True
        include_fk = True
        