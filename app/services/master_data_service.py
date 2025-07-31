from flask import request
from app import db
from app.models.entities.MasterData import MasterData
from app.schemas.master_data_schema import MasterDataSchema

def get_all_master_data():
    try:
        schema = MasterDataSchema(session=db.session, many=True)
        filter_data = request.args.to_dict()
        query = db.session.query(MasterData)
        
        if filter_data:
            for key, value in filter_data.items():
                if hasattr(MasterData, key) and value.strip("'") != '':
                    query = query.filter(getattr(MasterData, key) == value.strip("'"))
        
        results = query.all()
        return schema.dump(results), 200
        
    except Exception as e:
        return {"error": str(e)}, 500
    
def get_master_data_by_catalog(NAME, CODE=""):
    try:
        schema = MasterDataSchema(session=db.session)
        results = db.session.query(MasterData).filter(MasterData.catalog_code == NAME, MasterData.code == CODE).first()
        
        if not results:
            return {"message": "No data found for the given catalog code"}, 404
            
        return schema.dump(results), 200
        
    except Exception as e:
        return {"error": str(e)}, 500

def create_master_data():
    try:
        data = request.get_json()
        schema = MasterDataSchema(session=db.session)
        
        errors = schema.validate(data)
        if errors:
            return {"errors": errors}, 400
            
        new_master_data = MasterData(**data)
        db.session.add(new_master_data)
        db.session.commit()
        
        return schema.dump(new_master_data), 201
        
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def update_master_data(id):
    try:
        data = request.get_json()
        schema = MasterDataSchema(session=db.session)
        
        master_data = MasterData.query.get(id)
        if not master_data:
            return {"error": "MasterData not found"}, 404
            
        for key, value in data.items():
            setattr(master_data, key, value)
            
        db.session.commit()
        return schema.dump(master_data), 200
        
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def delete_master_data(id):
    try:
        master_data = MasterData.query.get(id)
        if not master_data:
            return {"error": "MasterData not found"}, 404
            
        db.session.delete(master_data)
        db.session.commit()
        return {"message": "MasterData deleted successfully"}, 200
        
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def get_master_data_by_id(id):
    try:
        master_data = MasterData.query.get(id)
        if not master_data:
            return {"error": "MasterData not found"}, 404
            
        return MasterDataSchema(session=db.session).dump(master_data), 200
    except Exception as e:
        return {"error": str(e)}, 500

def generacion_factura_dummy():
    try:
        data = request.get_json()
        return "result", 200
    except Exception as e:
        return {"error2": str(e)}, 500



