import pytest
from app.services.product_service import create_product, get_all_products, update_product, delete_product
from app.models.entities.Product import Product

def test_get_all_products(client, db_session):
    # Arrange
    product = Product(
        name="Test Product",
        price=100.0,
        stock_inicial=10,
        stock_actual=10,
        id_status=23
    )
    db_session.add(product)
    db_session.commit()

    # Act
    response = client.get('/api/products/')

    # Assert
    assert response.status_code == 200
    # assert len(response.json) >= 1
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(p['name'] == "Test Product" for p in data)


def test_create_product(client, db_session):
    # Arrange
    product_data = {
        "name": "New Product",
        "price": 150.0,
        "stock_inicial": 20,
        "stock_actual": 20,
        "id_status": 23
    }

    # Act
    response = client.post('/api/products/', json=product_data)

    # Assert
    assert response.status_code == 201
    assert response.json['name'] == product_data['name']