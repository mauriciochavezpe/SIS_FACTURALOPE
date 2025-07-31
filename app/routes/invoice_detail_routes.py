from flask_restx import Namespace, Resource, fields
from app.services.invoice_detail_service import (
    get_invoice_details_all,
    create_invoice_detail,
    update_invoice_detail,
    delete_invoice_detail
)

invoice_detail_blueprint = Namespace('invoice_details', description='Invoice detail operations')

invoice_detail_model = invoice_detail_blueprint.model('InvoiceDetailModel', {
    'discount': fields.Float(description='The discount'),
    'product_id': fields.Integer(required=True, description='The product ID'),
    'quantity': fields.Integer(required=True, description='The quantity'),
    'subtotal': fields.Float(required=True, description='The subtotal'),
    'unit_price': fields.Float(required=True, description='The unit price'),
    'description':fields.String(required=False, description='The description'),
    'monto_total': fields.Float(required=True, description='The total amount')
})

@invoice_detail_blueprint.route('/')
class InvoiceDetailList(Resource):
    def get(self):
        details, status = get_invoice_details_all()
        return details, status

    @invoice_detail_blueprint.expect(invoice_detail_model)
    def post(self):
        detail, status = create_invoice_detail()
        return detail, status

@invoice_detail_blueprint.route('/<int:id>')
class InvoiceDetail(Resource):
    @invoice_detail_blueprint.expect(invoice_detail_model)
    def put(self, id):
        detail, status = update_invoice_detail(id)
        return detail, status

    def delete(self, id):
        result, status = delete_invoice_detail(id)
        return result, status

@invoice_detail_blueprint.route('/invoice/<int:invoice_id>')
class InvoiceDetailByInvoice(Resource):
    def get(self, invoice_id):
        details, status = get_invoice_details_all(invoice_id)
        return details, status