from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from app.models.entities.Storage import Storage

class StorageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Storage
        load_instance = True
        include_fk = True
    
    # id = auto_field()
    # file_name = auto_field()
    # file_path = auto_field()
    # file_type = auto_field()
    # file_size = auto_field()
    # eid_status = auto_field()
