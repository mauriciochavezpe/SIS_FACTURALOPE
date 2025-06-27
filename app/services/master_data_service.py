from flask import request
from app import db
from app.models.entities.MasterData import MasterData
from app.schemas.master_data_schema import MasterDataSchema
from app.utils.generar_xml import generar_xml, crear_xml_y_zip
from app.config.certificado import obtener_certificado, firmar_xml_con_placeholder
from datetime import datetime
from app.utils.conexion_sunat import (send_to_sunat, complete_data_xml)
from dotenv import load_dotenv
import requests
import base64
import time
import os


def get_all_master_data():
    try:
        schema = MasterDataSchema(session=db.session)
        filter = request.args.to_dict()
        query = db.session.query(MasterData)
        
        if filter:
            for key, value in filter.items():
                if hasattr(MasterData, key) and value.strip("'") != '':
                    query = query.filter(getattr(MasterData, key) == value.strip("'"))
        
        results = query.all()
        if not results:
            return [], 200
            
        return [schema.dump(item) for item in results], 200
        
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
        xml_firmado = complete_data_xml(data) # luego de completar los datos, se firma el XML


         
        # probar con sunat 
        # result = crear_xml_y_zip(xml_firmado,data)
        # path_xml = os.path.join('assets', '20603786590-01-F001-00000001.zip')
        result = send_to_sunat(xml_firmado,data)
        return result, 200
    except Exception as e:
        return {"error2": str(e)}, 500



