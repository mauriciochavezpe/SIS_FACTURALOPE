from flask_restx import Namespace, Resource, fields
from flask import request

from app import db
from app.services.invoice_service import (
    InvoiceCreationError, InvoiceNotFoundError, create_invoice_in_db,
    get_all_invoices, get_details_by_invoice, update_invoice_status)
from app.utils.sunat_client import SunatClientError, send_invoice_data_to_sunat

invoice_blueprint = Namespace('invoices', description='Invoice operations')

invoice_model = invoice_blueprint.model('InvoiceModel', {
    'document': fields.String(required=True, description='The document number (SERIE-NUMERO)'),
    'document_type': fields.Integer(required=True, description='The document type'),
    'ruc_cliente': fields.String(required=True, description='The customer RUC'),
    'date': fields.DateTime(required=True, description='The invoice date'),
    'relative_document': fields.String(description='The related invoice ID'),
    'codigo_table': fields.String(description='The related invoice ID'),
    'codigo_mensaje_table': fields.String(description='The related invoice ID'),
    'customer_id': fields.Integer(required=True, description='The product ID'),
    'subtotal': fields.Float(required=True, description='The subtotal'),
    'monto_igv': fields.Integer(required=True, description='The total amount'),
    'metodo_pago': fields.String(required=True, description='The total amount'),
    'quantity': fields.Integer(required=True, description='The total amount'),
    'afecto_tributo': fields.String(required=True, description='The total amount'),
    'details': fields.List(fields.Nested(invoice_blueprint.model('InvoiceDetailModel', {
        'discount': fields.Float(description='The discount'),
        'product_id': fields.Integer(required=True, description='The product ID'),
        'quantity': fields.Integer(required=True, description='The quantity'),
        'subtotal': fields.Float(required=True, description='The subtotal'),
        'unit_price': fields.Float(required=True, description='The unit price'),
        'description':fields.String(required=False, description='The description'),
        'monto_total': fields.Float(required=True, description='The total amount')
    })))
})

@invoice_blueprint.route('/')
class InvoiceList(Resource):
    def get(self):
        filters = request.args.to_dict()
        invoices = get_all_invoices(filters)
        return invoices, 200
@invoice_blueprint.route('/details/<int:id>')
class InvoiceDetails(Resource):
    def get(self, id):
        try:
            invoice_details = get_details_by_invoice(id)
            return invoice_details, 200
        except InvoiceNotFoundError as e:
            return {'error': str(e)}, 404


@invoice_blueprint.route('/send-to-sunat')
class InvoiceSend(Resource):
    @invoice_blueprint.expect(invoice_model)
    def post(self):
        data = request.get_json()
        if not data:
            return {"error": "No se proporcionaron datos en la solicitud."}, 400

        try:
            # invoice_obj = create_invoice_in_db(data)
            cdr_response = send_invoice_data_to_sunat(data)
            status_value = cdr_response.get("codigo_estado", "-1")
            update_invoice_status(data["document"], status_value, cdr_response)
            db.session.commit()

            return {
                "status": "success",
                "message": "Factura creada y enviada a SUNAT exitosamente.",
                "invoice_id": "invoice_obj.id",
                "sunat_response": cdr_response
            }, 201

        except (InvoiceCreationError, SunatClientError, InvoiceNotFoundError) as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        except Exception as e:
            db.session.rollback()
            return {"error": "Ocurrió un error interno inesperado."}, 500
