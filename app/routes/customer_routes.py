from flask_restx import Namespace, Resource, fields
from app.services.customer_service import (get_all_customers,
create_customer, get_customers_by_id, update_customers_by_id,get_customer_validate_by_ruc)

customer_blueprint = Namespace('customers', description='Customer operations')

customer_model = customer_blueprint.model('CustomerModel', {
    'username': fields.String(required=True, description='The customer username'),
    'email': fields.String(required=True, description='The customer email'),
    'password': fields.String(description='The customer password'),
    'phone': fields.String(description='The customer phone number'),
    'document_number': fields.String(required=True, description='The customer document number'),
    'is_business': fields.Boolean(description='Is the customer a business?'),
    'commercial_name': fields.String(description='The customer commercial name'),
    'business_name': fields.String(required=True, description='The customer business name'),
    'address': fields.String(description='The customer address'),
    'city': fields.String(description='The customer city'),
    'province': fields.String(description='The customer province'),
    'postal_code': fields.String(description='The customer postal code'),
    'country': fields.String(description='The customer country'),
    'full_name': fields.String(description='The customer full name'),
    'document_type': fields.String(required=True, description='The customer document type')
})

@customer_blueprint.route('')
class CustomerList(Resource):
    def get(self):
        customers,status = get_all_customers()
        return customers, status

    @customer_blueprint.expect(customer_model)
    def post(self):
        customers,status = create_customer()
        return customers, status

@customer_blueprint.route('/<int:user_id>')
class Customer(Resource):
    def get(self, user_id):
        """
        Validates a RUC if valid.
        """
        users,status = get_customers_by_id(user_id)
        return users, status

    @customer_blueprint.expect(customer_model)
    def put(self, user_id):
        users,status = update_customers_by_id(user_id)
        return users, status

@customer_blueprint.route('/validate_ruc/<string:ruc>')
class ValidateRUC(Resource):
    def get(self, ruc):
        """
        Validates a RUC number and returns customer data if valid.
        """
        try:
            customer_data = get_customer_validate_by_ruc(ruc)
            if isinstance(customer_data, dict) and "error" in customer_data:
                return customer_data, 500
            return customer_data, 200
        except Exception as e:
            return {"error": str(e)}, 500