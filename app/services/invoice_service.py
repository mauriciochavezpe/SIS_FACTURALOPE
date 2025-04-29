from flask import request
from app import db
from app.models.entities.Invoice import Invoice
from app.schemas.invoice_schema import InvoiceSchema
from datetime import datetime

def get_all_invoices():
    try:
        schema = InvoiceSchema(session=db.session)
        filter = request.args.to_dict()
        query = db.session.query(Invoice)
        
        if filter:
            for key, value in filter.items():
                if hasattr(Invoice, key) and value.strip("'") != '':
                    query = query.filter(getattr(Invoice, key) == value.strip("'"))
        
        results = query.all()
        if not results:
            return [], 200
            
        return [schema.dump(item) for item in results], 200
        
    except Exception as e:
        return {"error": str(e)}, 500

def create_invoice():
    try:
        data = request.get_json()
        schema = InvoiceSchema(session=db.session)
        
        # Validate input data
        errors = schema.validate(data)
        if errors:
            return {"errors": errors}, 400
            
        # Create new invoice
        new_invoice = Invoice(**data)
        new_invoice.date = datetime.utcnow()
        
        db.session.add(new_invoice)
        db.session.commit()
        
        return schema.dump(new_invoice), 201
        
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def update_invoice(id):
    try:
        data = request.get_json()
        schema = InvoiceSchema(session=db.session)
        
        invoice = Invoice.query.get(id)
        if not invoice:
            return {"error": "Invoice not found"}, 404
            
        # Update fields
        for key, value in data.items():
            setattr(invoice, key, value)
            
        db.session.commit()
        return schema.dump(invoice), 200
        
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def delete_invoice(id):
    try:
        invoice = Invoice.query.get(id)
        if not invoice:
            return {"error": "Invoice not found"}, 404
            
        db.session.delete(invoice)
        db.session.commit()
        return {"message": "Invoice deleted successfully"}, 200
        
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500