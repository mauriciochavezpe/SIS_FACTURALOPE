from flask import request
from app import db
from decimal import Decimal
from app.models.entities.Invoice import Invoice
from app.models.entities.InvoiceDetails import InvoiceDetail
from app.models.entities.Product import Product
from app.schemas.invoice_schema import InvoiceSchema
from app.models.entities.MasterData import MasterData
from app.schemas.invoice_detail_schema import InvoiceDetailSchema
from app.schemas.custom_detail_by_invoice_schema import ComplexInvoiceSchema
from datetime import datetime
from app.utils.sunat_client import (send_to_sunat)


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


def get_details_by_invoice(id):
    try:
        schema = InvoiceSchema(session=db.session)
        # invoice = Invoice.query.get(id)
        invoice = db.session.query(Invoice).join(InvoiceDetail, Invoice.id == InvoiceDetail.invoice_id).join(Product, InvoiceDetail.product_id == Product.id).filter(Invoice.id == id).first()
        # obtener la información del producto en el join
        print("invoice",invoice)
        if not invoice:
            return {"error": "Invoice not found"}, 404
        
        result = schema.dump(invoice)
        result['details'] = InvoiceDetailSchema(session=db.session, many=True).dump(invoice.invoice_details)
        return result, 200  

    except Exception as e:
        return {"error": str(e)}, 500

## definicion personalizada
def create_invoice_details():
    try:
        data = request.get_json()
        schema = ComplexInvoiceSchema(session=db.session)
        
        # Validate input data
        errors = schema.validate(data)
        if errors:
            return {"errors": errors}, 400
        
        ## create invoice
        invoice = Invoice(
            customer_id = data['customer_id'],
            num_invoice = data['num_invoice'],
            date = data['date'],
            id_status = 23,
            subtotal = 0,
            tax = 0,
            total = 0
        )
        db.session.add(invoice)
        # db.session.commit()
        db.session.flush()  # Obtener ID de la factura
        # realizar una consulta a la tabla master_data para obtener el valor de la tasa de IGV
        master_data = db.session.query(MasterData).filter_by(code_table='T_SUNAT', data_value='IGV').first()
        if not master_data:
            return {"error": "IGV rate not found in MasterData"}, 404
        
        igv_rate = Decimal(master_data.description_value)
        total_global = 0
        invoice_details = []
        # Create new invoice detail
        for detail in data['details']:

            if Decimal(detail['discount']) > 0:
                detail['subtotal'] -= Decimal(detail['discount'])
            
            detail['total'] = Decimal(detail['subtotal']) + (Decimal(igv_rate) * Decimal(detail['subtotal']))
            print("tax",igv_rate)     
            print("subtotal",detail['subtotal'])     
            print("total",detail['total'])     
            invoice_detail = InvoiceDetail(
                invoice_id = invoice.id,
                product_id = detail['product_id'],
                quantity = detail['quantity'],
                unit_price = detail['unit_price'],
                discount = detail['discount'] or 0.00,
                subtotal = detail['subtotal'],
                tax = igv_rate,
                total = detail['total']
            )
            
            total_global += invoice_detail.total

            invoice_details.append(invoice_detail)
        
        db.session.add_all(invoice_details)
        # db.session.commit()
        # calculamos el tota de la factura y procedemos a actualizar

        invoice.total = total_global
        db.session.commit()
        invoice_schema = InvoiceSchema()
        result = invoice_schema.dump(invoice)
        result['details'] = InvoiceDetailSchema(many=True).dump(invoice_details)
            
        return result, 201
        
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
    
def create_invoice_detail_sunat():
    try:
        data = request.get_json()
        result = send_to_sunat(data)
        return result, 200
    except Exception as e:
   
        return {"error": str(e)}, 500
    
def crear_factura_standard(data):
    try:
   
         ## create invoice
        invoice = Invoice(
            customer_id = data['customer_id'],
            num_invoice = data['num_invoice'],
            serie = data['serie'],
            date = data['date'],
            id_status = 23,
            subtotal = data['subtotal'] or 0,
            total = 0
        )
        db.session.add(invoice)
        db.session.flush()  # Obtener ID de la factura
        
    
        master_data = db.session.query(MasterData).filter_by(code_table='T_SUNAT', data_value='IGV').first()
        if not master_data:
            return {"error": "IGV rate not found in MasterData"}, 404
        igv_rate = Decimal(master_data.description_value)
        total_global = 0
        invoice_details = []
        invoice.tax = igv_rate
        # Create new invoice detail
        for detail in data['details']:

            if Decimal(detail['discount']) > 0:
                detail['subtotal'] -= Decimal(detail['discount'])
            
            detail['total'] = Decimal(detail['subtotal']) + (Decimal(igv_rate) * Decimal(detail['subtotal']))
            invoice_detail = InvoiceDetail(
                invoice_id = invoice.id,
                product_id = detail['product_id'],
                quantity = detail['quantity'],
                unit_price = detail['unit_price'],
                discount = detail['discount'] or 0.00,
                subtotal = detail['subtotal'],
                tax = igv_rate,
                total = detail['total']
            )
            
            total_global += invoice_detail.total

            invoice_details.append(invoice_detail)
        db.session.add_all(invoice_details)
        # db.session.commit()
        # calculamos el tota de la factura y procedemos a actualizar

        invoice.total = total_global
        db.session.commit()
        invoice_schema = InvoiceSchema()
        result = invoice_schema.dump(invoice)
        result['details'] = InvoiceDetailSchema(many=True).dump(invoice_details)
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500