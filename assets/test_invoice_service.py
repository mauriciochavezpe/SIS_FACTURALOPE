import pytest
from app.services.invoice_service import create_invoice, get_all_invoices
from app.models.entities.Invoice import Invoice
from app.models.entities.Customer import Customer

def test_create_invoice(client, db_session):
    # Arrange
    customer = Customer(
        business_name="Test Customer",
        document_type="6",
        document_number="20123456789"
    )
    db_session.add(customer)
    db_session.commit()

    invoice_data = {
        "customer_id": customer.id,
        "total": 100.0,
        "id_status": 23,
        "tax": 12.0,
        "discount": 10.0,
        "total_with_discount": 90.0  
    }

    # Act
    response = client.post('/api/invoices/', json=invoice_data)

    # Assert
    assert response.status_code == 201
    assert response.json['customer_id'] == customer.id