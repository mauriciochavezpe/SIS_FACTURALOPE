from flask import request
from app.models.entities.Product import Product
from app.schemas.product_schema import ProductSchema
from app.extension import db
from datetime import datetime

def get_all_products():
    schema = ProductSchema(session=db.session, many=True)
    filter_data = request.args.to_dict()
    query = db.session.query(Product)
    try:
        if filter_data:
            for key, value in filter_data.items():
                if hasattr(Product, key) and value.strip("'") != '':
                    query = query.filter(getattr(Product, key) == value.strip("'"))
                    
        query = query.filter(Product.id_status == 23)
        
        results = query.all()
        return schema.dump(results), 200
    except Exception as e:
        return {"error": str(e)}, 500

def create_product():
    try:
        data = request.get_json()
        schema = ProductSchema(session=db.session)
        
        errors = schema.validate(data)
        if errors:
            return {"errors": errors}, 400
        
        new_product = Product(**data)
        new_product.createdAt = datetime.now()
        new_product.createdBy = data.get("user","SYSTEM")
        new_product.ip = request.remote_addr
        
        db.session.add(new_product)
        db.session.commit()
        
        return schema.dump(new_product), 201
    except Exception as e:
        return {"error": str(e)}, 500
    
def update_product(id):
    try:
        data = request.get_json()
        schema = ProductSchema(session=db.session)
        
        errors = schema.validate(data)
        if errors:
            return {"errors": errors}, 400
        
        product = Product.query.get(id)
        if not product:
            return {"error": "Producto no encontrado"}, 404
        
        for key, value in data.items():
            setattr(product, key, value)
        
        product.modifiedAt = datetime.now()
        product.modifiedBy = data.get("user","SYSTEM")
        product.ip = request.remote_addr
           
        db.session.commit()
        
        return schema.dump(product), 200
    except Exception as e:
        return {"error": str(e)}, 500

def delete_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            return {"error": "Producto no encontrado"}, 404
        product.id_status = 25
        product.modifiedAt = datetime.now()
        product.modifiedBy = data.get("user","SYSTEM")
        product.ip = request.remote_addr
        db.session.commit()
        
        return {"message": "Producto eliminado"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
