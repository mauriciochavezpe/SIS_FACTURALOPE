from app.models.enums.document_types import DocumentType
from app.schemas.customer_schema import CustomerSchema
from app.extension import db
from app.models.entities.Customer import Customer
from flask import request, jsonify
from sqlalchemy import Boolean
def create_customer():
    try:
        data = request.get_json()
        schema = CustomerSchema(session=db.session)
        # validated_data = schema.load(data)
        print(f"data: {schema}")
        # Validate document number format
        if not DocumentType.validate_document(data['document_type'], data['document_number']):
            return {
                "error": "Invalid document number format for the selected document type"
            }, 400
        
        new_customer = Customer(**data) 
        print(f"new_customer: {new_customer}")
        db.session.add(new_customer)
        db.session.commit()
        return schema.dump(new_customer), 201
        
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
 
def get_all_customers():
    try:
        filter = request.args.to_dict()
        query = db.session.query(Customer)
        
        # Aplicar filtros si están presentes
        for key, value in filter.items():
            print(f'Filtering by {key}: {value}')
            if hasattr(Customer, key):
                query = query.filter(getattr(Customer, key) == value)
        
        results = query.all()
        print(f'Total customers found: {len(results)}')
        if not results:
            return [], 200
        
        schema = CustomerSchema(session=db.session, many=True)
        serialized_results = schema.dump(results)
        print(f'Serialized results: {serialized_results}')
        return serialized_results, 200

    except Exception as e:
        return {"error": str(e)}, 500

def get_customers_by_id(user_id):
    try:
        customer = db.session.query(Customer).filter_by(id=user_id).first()
        if not customer:
            return {"error": "Customer not found"}, 404
        schema = CustomerSchema(session=db.session)
        return schema.dump(customer), 200
    except Exception as e:
        return {"error": str(e)}, 500

def update_customers_by_id(user_id):
    try:
        customer = db.session.query(Customer).filter_by(id=user_id).first()
        if not customer:
            return {"error": "Customer not found"}, 404
        data = request.get_json()
        for key, value in data.items():
            setattr(customer, key, value)
        db.session.commit()
        schema = CustomerSchema(session=db.session)
        return schema.dump(customer), 200
    except Exception as e:
        return {"error": str(e)}, 500
    
def get_all_customers_by_ruc(rucs):
    
    try:
        # for ruc in rucs:
            # if len(ruc) != 11:
            #     ""
            #     # return {"error": f"La longitud del RUC {ruc} debe ser de 11 dígitos"}, 400
            # else:
            #     if not ruc.isdigit():
            #         return {"error": f"El RUC {ruc} debe contener solo dígitos"}, 400
        query = db.session.query(Customer).filter(Customer.document_number.in_(rucs))
        
        # Filtrar por todos los RUCs usando in_
        
        
        results = query.all()
        if not results:
            return [], 200
        # print(f"results: {results}")
        # print(f"results ln: {len(results)}")
        schema = CustomerSchema(session=db.session, many=True)
        return schema.dump(results), 200

    except Exception as e:
        return {"error": str(e)}, 500