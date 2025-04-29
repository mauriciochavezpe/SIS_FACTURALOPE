from app.models.enums.document_types import DocumentType

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
        # if 'status_id' not in data:
        #     data['status_id'] = CustomerStatus.ACTIVE.id
            
        # ...existing code...
        
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500