import sys
import os
import pytest
from datetime import datetime
from app.models.entities.Product import Product

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extension import db

@pytest.fixture(scope='session')
def app():
    """Create and configure a test application instance."""
    app = create_app()
    # app.config.update({
    #     'TESTING': True,
    #     'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:123456@localhost:5432/Facturacion',
    #     'SQLALCHEMY_TRACK_MODIFICATIONS': False
    # })
    return app

@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Create a fresh database for each test."""
    with app.app_context():
        db.create_all()
        
        # Add any initial test data here
         # Create test data
        test_product = Product(
            name="Test Product",
            price=100.0,
            stock_inicial=10,
            stock_actual=10,
            id_status=23
        )
        db.session.add(test_product)
        db.session.commit()
        yield db
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def auth_headers():
    """Fixture for authentication headers."""
    return {'Authorization': 'Bearer test-token'}