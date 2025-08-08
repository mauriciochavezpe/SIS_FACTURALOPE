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

def test_update_product(client, db_session):
    # Arrange
    product = Product(
        name="Update Product",
        price=200.0,
        stock_inicial=30,
        stock_actual=30,
        id_status=23
    )
    db_session.add(product)
    db_session.commit()

    update_data = {"price": 250.0}

    # Act
    response = client.put(f'/api/products/{product.id}', json=update_data)

    # Assert
    assert response.status_code == 200
    assert response.json['price'] == update_data['price']

def test_delete_product(client, db_session):
    # Arrange
    product = Product(
        name="Delete Product",
        price=300.0,
        stock_inicial=40,
        stock_actual=40,
        id_status=23
    )
    db_session.add(product)
    db_session.commit()

    # Act
    response = client.delete(f'/api/products/{product.id}')

    # Assert
    assert response.status_code == 200
    assert response.json['message'] == "Producto eliminado"


def test_create_product_invalid_data(client):
    # Arrange
    # Missing 'name' which is likely required
    product_data = {
        "price": 150.0,
        "stock_inicial": 20,
        "stock_actual": 20,
        "id_status": 23
    }

    # Act
    response = client.post('/api/products/', json=product_data)

    # Assert
    assert response.status_code == 400
    assert "errors" in response.json

def test_update_product_not_found(client):
    # Arrange
    update_data = {"price": 999.00}
    non_existent_id = 99999

    # Act
    response = client.put(f'/api/products/{non_existent_id}', json=update_data)
    
    # Assert
    assert response.status_code == 404
    assert response.json['error'] == "Producto no encontrado"

def test_delete_product_not_found(client):
    # Arrange
    non_existent_id = 99999

    # Act
    response = client.delete(f'/api/products/{non_existent_id}')

    # Assert
    assert response.status_code == 404
    assert response.json['error'] == "Producto no encontrado"

def test_get_all_products_with_filter(client, db_session):
    # Arrange
    product1 = Product(name="Filter Test Product One", price=10.0, stock_inicial=1, stock_actual=1, id_status=23)
    product2 = Product(name="Filter Test Product Two", price=20.0, stock_inicial=2, stock_actual=2, id_status=23)
    db_session.add_all([product1, product2])
    db_session.commit()

    # Act
    response = client.get('/api/products/?name=Filter Test Product One')

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == "Filter Test Product One"
