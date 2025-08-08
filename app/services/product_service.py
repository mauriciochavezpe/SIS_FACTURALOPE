from flask import request
from app.models.entities.Product import Product
from app.schemas.product_schema import ProductSchema
from app.extension import db
from datetime import datetime
from app.utils.catalog_manager import catalog_manager
from app.constants.catalog_constants import (CATALOG_STATUS,STATUS_ACTIVE)

def get_all_products():
    schema = ProductSchema(session=db.session, many=True)
    filter_data = request.args.to_dict()
    query = db.session.query(Product)
    
    try:
        if filter_data:
            for key, value in filter_data.items():
                if hasattr(Product, key) and value.strip("'") != '':
                    query = query.filter(getattr(Product, key) == value.strip("'"))
                    
        active_status_id = catalog_manager.get_id(CATALOG_STATUS, STATUS_ACTIVE)
        print("active_status_id",active_status_id)
        if active_status_id:
            query = query.filter(Product.id_status == active_status_id)
        
        results = query.all()
        return schema.dump(results), 200
    except Exception as e:
        return {"error": str(e)}, 500

def create_product():
    try:
        data = request.get_json()
        schema = ProductSchema(session=db.session)
        print("data",data)
        errors = schema.validate(data)
        print("errors",errors)
        if errors:
            return {"errors": errors}, 400
        
        new_product = Product(**data)
        active_status_id = catalog_manager.get_id(CATALOG_STATUS, STATUS_ACTIVE)
        new_product.id_status = active_status_id
        new_product.createdAt = datetime.now()
        new_product.createdBy = request.headers.get("user", "system")
        new_product.ip = request.remote_addr
        
        db.session.add(new_product)
        db.session.commit()
        
        return schema.dump(new_product), 201
    except Exception as e:
        return {"error": str(e)}, 500
    
def update_product(id):
    try:
        data = request.get_json()
        schema = ProductSchema(session=db.session, partial=True)
        
        errors = schema.validate(data)
        if errors:
            return {"errors": errors}, 400
        product = db.session.get(Product, id)
        if not product:
            return {"error": "Producto no encontrado"}, 404
        
        for key, value in data.items():
            setattr(product, key, value)
        
        product.modifiedAt = datetime.now()
        product.modifiedBy = request.headers.get("user", "system")
        product.ip = request.remote_addr
           
        db.session.commit()
        
        return schema.dump(product), 200
    except Exception as e:
        return {"error": str(e)}, 500

def delete_product(id):
    try:
        product = db.session.get(Product, id)
        if not product:
            return {"error": "Producto no encontrado"}, 404
        
        # deleted_status_id = catalog_manager.get_id(Constantes.CATALOG_PRODUCT_STATUS, Constantes.STATUS_DELETED)
        # if deleted_status_id:
        #     product.id_status = deleted_status_id
        product.id_status = 1
        product.modifiedAt = datetime.now()
        product.modifiedBy = request.headers.get("user", "system")
        product.ip = request.remote_addr
        db.session.commit()
        
        return {"message": "Producto eliminado"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

