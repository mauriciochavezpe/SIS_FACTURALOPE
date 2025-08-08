from app.models.enums.document_types import DocumentType
from app.schemas.customer_schema import CustomerSchema
from app.extension import db
from app.models.entities.Customer import Customer
from flask import request
from datetime import datetime
from app.utils.catalog_manager import catalog_manager
import requests
import os

def validar_ruc(ruc):
    try:
        """
        Valida el RUC peruano.
        
        Args:
            ruc (str): RUC a validar.
            
        Returns:
            bool: True si el RUC es válido, False en caso contrario.
        """
        url_request = os.getenv("VALIDAR_RUC_SUNAT")
        url_request = url_request.replace("XXXXX", ruc)
    
        response = requests.get(url_request, timeout=10)
        payload = response.json()
        # print("payload",payload)
        if("error" in payload):
            print("❌ Error al validar RUC:", payload["error"])
            # return {"error": payload["error"]}, 500
            raise ValueError(payload["error"])
        else:
            cliente = payload.get("lista", [])
            # quitar los espacios en blanco
            if cliente and isinstance(cliente[0], dict):
                cliente[0] = {k: v.strip() if isinstance(v, str) else v for k, v in cliente[0].items()}
            return cliente
    # return response
    except Exception as e:
        print(f"❌ Error al validar RUC: {e}")
        return {"error": str(e)}, 500

def parse_customer_data(data: list) -> dict:
     """
     Convierte los datos del cliente de la respuesta del servicio de RUC
     a un diccionario compatible con el modelo Customer.
     """
     if not data or not isinstance(data, list) or not data[0]:
         return {}

     source = data[0]

     # Mapeo de los campos del servicio a los campos del modelo Customer
     customer_dict = {
         'business_name': source.get('apenomdenunciado'),
         'address': source.get('direstablecimiento'),
         'province': source.get('desprovincia'),
         'city': source.get('desdistrito'),
         'country': source.get('desdepartamento'),
         # El document_number (RUC) no viene en este payload,
         # se debe añadir desde la variable que ya se tiene en el servicio.
     }
     return customer_dict

def create_customer():
    try:
        data = request.get_json()
        password = data.pop('password_hash', None)
        if not password:
            return {"error": "Password is required"}, 400
        parse_num_type = f"{int(data.get('document_type')):02d}"
        print(f"parse_num_type: {parse_num_type}")
        if not DocumentType.validate_document(parse_num_type, data['document_number']):
            return {
                "error": "Invalid document number format for the selected document type"
            }, 400
        
        schema = CustomerSchema(session=db.session, exclude=['password_hash'])
        new_customer = schema.load(data)
        new_customer.set_password(password)
        new_customer.createdAt = datetime.now()
        new_customer.createdBy = data.get("user","SYSTEM")
        new_customer.ip = request.remote_addr
        # new_customer.id_status = catalog_manager.get_id(Constantes.CATALOG_USER_STATUS,Constantes.STATUS_ACTIVE)  # Default to active status
        db.session.add(new_customer)
        db.session.commit()
        return schema.dump(new_customer), 201
        
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
 
def get_all_customers():
    try:
        filter_data = request.args.to_dict()
        query = db.session.query(Customer)
        
        for key, value in filter_data.items():
            if hasattr(Customer, key):
                query = query.filter(getattr(Customer, key) == value)
        
        results = query.all()
        
        schema = CustomerSchema(session=db.session, many=True)
        return schema.dump(results), 200

    except Exception as e:
        return {"error": str(e)}, 500

def get_customers_by_id(user_id):
    try:
        schema = CustomerSchema(session=db.session)
        customer = db.session.query(Customer).filter_by(id=user_id).first()
        if customer:
            return schema.dump(customer), 200
        else:
            return {"error": "Customer not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

def update_customers_by_id(user_id):
    try:
        customer = db.session.query(Customer).filter_by(id=user_id).first()
        if not customer:
            return {"error": "Customer not found"}, 404
        data = request.get_json()

        if 'password' in data:
            password = data.pop('password')
            customer.set_password(password)

        for key, value in data.items():
            setattr(customer, key, value)
        
        customer.modifiedAt = datetime.now()
        customer.modifiedBy = data.get("user","SYSTEM")
        customer.ip = request.remote_addr

        db.session.commit()
        schema = CustomerSchema(session=db.session)
        return schema.dump(customer), 200
    except Exception as e:
        return {"error": str(e)}, 500
    
def get_all_customers_by_ruc(rucs):
    
    try:
        query = db.session.query(Customer).filter(Customer.document_number.in_(rucs))
        
        results = query.all()
        if not results:
            return [], 200
        schema = CustomerSchema(session=db.session, many=True)
        return schema.dump(results), 200

    except Exception as e:
        return {"error": str(e)}, 500

## vamos a buscar un cliente por si no existe en VALIDAR_RUC_SUNAT
def get_customer_validate_by_ruc(ruc):
    try:
        customer = db.session.query(Customer).filter_by(document_number=ruc).first()
        if not customer:
            customer_data_ext=validar_ruc(ruc)  # Esto lanzará una excepción si el RUC no es válido
            customer= parse_customer_data(customer_data_ext)
            if isinstance(customer, dict) and "error" in customer:
                return {"error": "Customer not found"}, 404
            else:
                customer['document_number'] = ruc
                
        print("customer", customer)
        schema = CustomerSchema(session=db.session)
        return schema.dump(customer), 200
    except Exception as e:
        return {"error": str(e)}, 500