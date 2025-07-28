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
        import logging
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500

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
        
    except (ValueError, KeyError, AttributeError) as e:
        db.session.rollback()
        return {"error": str(e)}, 500
    except SQLAlchemyError as e:
        import logging
        db.session.rollback()
        logging.error(f"Database error: {str(e)}", exc_info=True)
        return {"error": f"Database error occurred: {str(e)}"}, 500

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
        import logging
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        db.session.rollback()
        return {"error": str(e)}, 500
    
def update_invoice_status(documento,value):
    try:
        schema = InvoiceSchema(session=db.session)
        master_data = db.session.query(MasterData).filter_by(catalog_code='T_ESTADO_SOLICITUD').all()
        # buscar value en master_data
        bflag_sts = False
        if master_data:
            for master in master_data:
                if master.value == value:
                    status_code = master.code
                    bflag_sts = True
                    break
        # else:
            # return {"error": "MasterData not found for T_ESTADO_SOLICITUD"}, 404
        serie = documento.split("-")[0]
        correlativo = int(documento.split("-")[1])
        num_invoice = f"{correlativo:08d}"
        invoice = Invoice.query.filter_by(serie=serie, num_invoice=num_invoice).first()
        if not invoice:
            return {"error": "Invoice not found"}, 404
            
        # Update fields
        if bflag_sts:
            invoice.id_status = status_code
           
        
        # else:
        #     return {"error": "Invalid status value provided"}, 400
        
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
            return {"error": f"IGV rate not found in MasterData for catalog_code='T_SUNAT' and code='IGV'"}, 404
        
        igv_rate = Decimal(master_data.description_value)
        total_global = 0
        invoice_details = []
        # Create new invoice detail
        for detail in data['details']:

            if detail['discount']:
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
        
        # Add all invoice details to the session in one operation
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
    

#aqui
def create_invoice_detail_sunat():
    try:
        data = request.get_json()

        # 1. Crear la factura localmente
        payload, status = crear_factura_standard(data)

        if isinstance(payload, dict) and "error" in payload:
            return payload, status  # Error al crear factura, termina el flujo

        # 2. Enviar a SUNAT
        payload_sunat, status_sunat = send_to_sunat(data)

        if status_sunat >= 200 and status_sunat < 300:
            codigo_estado = payload_sunat.get("codigo_estado")
            if codigo_estado:
                # 3. Actualizar estado de la factura en BD
                updated_payload = update_invoice_status(data["document"], codigo_estado)
                return updated_payload, 200
            else:
                return {"error": "Falta el campo 'codigo_estado' en la respuesta de SUNAT"}, 400
        else:
            return {
                "error": f"Error al enviar a SUNAT. Código de estado HTTP: {status_sunat}",
                "detalle": payload_sunat
            }, 400

    except Exception as e:
        return {"error": str(e)}, 500

def crear_factura_standard(data):
    try:
        document_parts = data['document'].split('-')
        if len(document_parts) != 2 or not document_parts[1].isdigit():
                return {"error": "Se esperaba un 'SERIE-NUMERIC' format."}, 400
        documento = data.get("document", "")
        if "-" not in documento:
            return {"error": "Formato de documento inválido. Debe ser 'SERIE-NUMERO'"}, 400

        serie, numero_str = documento.split("-")
        correlativo = int(numero_str)

        # Crear factura base
        invoice = Invoice(
            customer_id=data.get("customer_id"),
            num_invoice=f"{correlativo:08d}",
            serie=serie,
            document_type=data.get("type_document"),
            date=data.get("date"),
            id_status=25,  # Pendiente de envío a SUNAT
            subtotal=Decimal(data.get("subtotal", 0) or 0),
            total=Decimal("0.00")  # Se calcula después
        )
        db.session.add(invoice)
        db.session.flush()  # Obtener ID antes del commit

        # Obtener porcentaje IGV desde catálogo
        igv_entry = MasterData.query.filter_by(catalog_code='T_SUNAT', code='IGV').first()
        if not igv_entry:
            return {"error": "No se encontró tasa IGV en MasterData"}, 404
        igv_rate = Decimal(igv_entry.value or "0") / 100

        invoice.tax = igv_rate

        total_factura = Decimal("0.00")
        detalles_factura = []

        detalles = data.get("details", [])
        if not detalles:
            return {"error": "Debe proporcionar al menos un detalle de factura"}, 400

        for item in detalles:
            cantidad = Decimal(item.get("quantity", 1))
            precio_unitario = Decimal(item.get("unit_price", 0))
            descuento = Decimal(item.get("discount", 0))

            subtotal = (cantidad * precio_unitario) - descuento
            igv_monto = subtotal * igv_rate
            total = subtotal + igv_monto

            detalle = InvoiceDetail(
                invoice_id=invoice.id,
                product_id=item["product_id"],
                quantity=cantidad,
                unit_price=precio_unitario,
                discount=descuento,
                subtotal=subtotal,
                tax=igv_monto,
                total=total
            )

            detalles_factura.append(detalle)
            total_factura += total

        db.session.add_all(detalles_factura)
        invoice.total = total_factura

        db.session.commit()

        # Serialización final
        invoice_schema = InvoiceSchema()
        result = invoice_schema.dump(invoice)
        result["details"] = InvoiceDetailSchema(many=True).dump(detalles_factura)

        return result, 201

    except Exception as e:
        db.session.rollback()
        # current_app.logger.error(f"❌ Error al crear factura: {e}")
        return {"error": "Error al crear la factura", "detalle": str(e)}, 500


     