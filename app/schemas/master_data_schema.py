from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.entities.MasterData import MasterData

class MasterDataSchema(SQLAlchemySchema):
    class Meta:
        model = MasterData
        load_instance = True
        include_fk = True
    
    id = auto_field()
    catalog_code = auto_field()
    code = auto_field()
    value = auto_field()
    description = auto_field()
    is_active = auto_field()
    status_id = auto_field()
    extra = auto_field()