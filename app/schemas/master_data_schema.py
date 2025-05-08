from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.entities.MasterData import MasterData

class MasterDataSchema(SQLAlchemySchema):
    class Meta:
        model = MasterData
        load_instance = True
        include_fk = True
    
    id = auto_field()
    code_table = auto_field()
    data_value = auto_field()
    description_value = auto_field()
    is_active = auto_field()