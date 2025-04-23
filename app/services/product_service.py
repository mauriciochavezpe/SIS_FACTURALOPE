from flask import jsonify, request
from app.models.Product import Product
from datetime import datetime
# from app.utils.utils import getIP
from app.schemas.product_schema import ProductSchema
from app.extension import db
# from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
# from app.auth.jwt_handler import generate_jwt


def get_all_products():
    schema = ProductSchema(session=db.session)
    filter = request.args.to_dict()
    query = db.session.query(Product)
    print(f"filter: {filter}")  
    try:
        
        if filter:
            for key, value in filter.items():
                if hasattr(Product, key) and value.strip("'") != '':
                    query = query.filter(getattr(Product, key) == value.strip("'"))
                    
        query.filter(Product.estatus_id == 23)
        
        results = query.all()
        if not results:
            return results, 200
        
        print(f"results: {results}")
        serialized_results = [schema.dump(item) for item in results]
        print(f"serialized_results: {serialized_results}")
        
        return serialized_results, 200
    except Exception as e:
        return {"error": str(e)}, 500

def create_product():
    try:
        data = request.get_json()
        print(f"data: {data}")
        schema = ProductSchema(session=db.session)
        
        # Validar los datos de entrada
        errors = schema.validate(data)
        print(f"errors: {errors}")
        if errors:
            return {"errors": errors}, 400
        
        # Crear un nuevo producto
        new_product = Product(**data)
        # deseo agregar el campo ip
        # new_product.ip = getIP()
        # new_product.created_at = datetime.now()
        
        # Guardar en la base de datos
        db.session.add(new_product)
        db.session.commit()
        
        return schema.dump(new_product), 201
    except Exception as e:
        return {"error": str(e)}, 500
    
def update_product(id):
    try:
        data = request.get_json()
        print(f"data: {data}")
        schema = ProductSchema(session=db.session)
        
        # Validar los datos de entrada
        errors = schema.validate(data)
        print(f"errors: {errors}")
        if errors:
            return {"errors": errors}, 400
        
        # Obtener el producto por su ID
        product = Product.query.get(id)
        if not product:
            return {"error": "Producto no encontrado"}, 404
        
        # Actualizar los campos del producto con los datos de entrada
        for key, value in data.items():
            setattr(product, key, value)
           
        # product.updated_at = datetime.now()
        # product.ip = getIP()
        
        # Guardar los cambios en la base de datos
        db.session.commit()
        
        return schema.dump(product), 200
    except Exception as e:
        return {"error": str(e)}, 500

def delete_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            return {"error": "Producto no encontrado"}, 404
        product.estatus_id = 25
        # db.session.delete(product)
        db.session.commit()
        
        return {"message": "Producto eliminado"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

