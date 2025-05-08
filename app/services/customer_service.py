from app.models.enums.document_types import DocumentType
from app.schemas.customer_schema import CustomerSchema
from app.extension import db
from app.models.entities.Customer import Customer
from flask import request, jsonify
def create_customer():
    try:
        data = request.get_json()
        schema = CustomerSchema(session=db.session)
        
        # Validate document number format
        if not DocumentType.validate_document(data['document_type'], data['document_number']):
            return {
                "error": "Invalid document number format for the selected document type"
            }, 400
        
        # Set default status if not provided
        # if 'id_status' not in data:
        #     data['id_status'] = CustomerStatus.ACTIVE.id
            
        # ...existing code...
        
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
    
def get_all_customers():
    try:
        schema = CustomerSchema(session=db.session)
        filter = request.args.to_dict()
        query = db.session.query(Customer)
        
        if filter:
            for key, value in filter.items():
                if hasattr(Customer, key) and value.strip("'") != '':
                    query = query.filter(getattr(Customer, key) == value.strip("'"))
                    
        query.filter(Customer.id_status == 23)
        
        results = query.all()
        if not results:
            return results, 200
        
        return jsonify([schema.dump(item) for item in results]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500