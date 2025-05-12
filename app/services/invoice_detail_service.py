from flask import request
from app import db
from app.models.entities.InvoiceDetails import InvoiceDetail
from app.schemas.invoice_detail_schema import InvoiceDetailSchema
from decimal import Decimal

def get_invoice_details_all(invoice_id=None):
    try:
        schema = InvoiceDetailSchema(session=db.session)
        query = InvoiceDetail.query
        
        if invoice_id:
            query = query.filter_by(invoice_id=invoice_id)
            
        results = query.all()
        return [schema.dump(item) for item in results], 200
    except Exception as e:
        return {"error": str(e)}, 500

def create_invoice_detail():
    try:
        data = request.get_json()
        schema = InvoiceDetailSchema(session=db.session)
        
        # Validate data
        errors = schema.validate(data)
        if errors:
            return {"errors": errors}, 400
            
        # Calculate totals
        quantity = Decimal(str(data['quantity']))
        unit_price = Decimal(str(data['unit_price']))
        discount = Decimal(str(data.get('discount', 0)))
        
        subtotal = quantity * unit_price - discount
        tax = subtotal * Decimal('0.18')  # IGV 18%
        total = subtotal + tax
        
        # Add calculated fields
        data.update({
            'subtotal': float(subtotal),
            'tax': float(tax),
            'total': float(total)
        })
        
        detail = InvoiceDetail(**data)
        db.session.add(detail)
        db.session.commit()
        
        return schema.dump(detail), 201
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def update_invoice_detail(id):
    try:
        data = request.get_json()
        schema = InvoiceDetailSchema(session=db.session)
        
        detail = InvoiceDetail.query.get(id)
        if not detail:
            return {"error": "Detail not found"}, 404
            
        # Update fields and recalculate totals
        for key, value in data.items():
            setattr(detail, key, value)
            
        if 'quantity' in data or 'unit_price' in data or 'discount' in data:
            discount = detail.discount or 0
            quantity = detail.quantity
            unit_price = detail.unit_price
            print(quantity, unit_price, discount)
            detail.subtotal = float(quantity * unit_price - discount)
            print(detail.subtotal)
            detail.tax = float(detail.subtotal * 0.18)
            print(detail.tax)
            detail.total = float(detail.subtotal + detail.tax)
            # print(detail.total)        
        db.session.commit()
        return schema.dump(detail), 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def delete_invoice_detail(id):
    try:
        detail = InvoiceDetail.query.get(id)
        if not detail:
            return {"error": "Detail not found"}, 404
            
        db.session.delete(detail)
        db.session.commit()
        return {"message": "Detail deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500