from app.models.enums.document_types import DocumentType
from app.schemas.customer_schema import CustomerSchema
from app.extension import db
from app.models.entities.Customer import Customer
from flask import request
from datetime import datetime
from app.utils.catalog_manager import catalog_manager
from app.utils.utils_constantes import Constantes
def create_customer():
    try:
        data = request.get_json()
        password = data.pop('password', None)
        if not password:
            return {"error": "Password is required"}, 400

        if not DocumentType.validate_document(data['document_type'], data['document_number']):
            return {
                "error": "Invalid document number format for the selected document type"
            }, 400
        
        schema = CustomerSchema(session=db.session, exclude=['password_hash'])
        new_customer = schema.load(data)
        new_customer.set_password(password)
        new_customer.createdAt = datetime.now()
        new_customer.createdBy = data.get("user","SYSTEM")
        new_customer.ip = request.remote_addr
        new_customer.id_status = catalog_manager.get_id(Constantes.CATALOG_USER_STATUS,Constantes.STATUS_ACTIVE)  # Default to active status
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
