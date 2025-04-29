from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.entities.Storage import Storage

class StorageSchema(SQLAlchemySchema):
    class Meta:
        model = Storage
        load_instance = True
        include_fk = True
    
    id = auto_field()
    file_name = auto_field()
    file_path = auto_field()
    file_type = auto_field()
    file_size = auto_field()
    estatus_id = auto_field()
    created_at = auto_field()
    updated_at = auto_field()
