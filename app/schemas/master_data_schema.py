from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from app.models.entities.MasterData import MasterData

class MasterDataSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MasterData
        load_instance = True
        include_fk = True
    