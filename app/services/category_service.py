from flask import jsonify, request
from app.models.entities.Category import Category
from datetime import datetime
# from app.utils.utils import getIP
from app.schemas.category_schema import CategorySchema
from app.extension import db



def get_all_categories():
    schema = CategorySchema(session=db.session)
    filter = request.args.to_dict()
    query = db.session.query(Category)
    print(f"filter: {filter}")  
    try:
        
        if filter:
            for key, value in filter.items():
                if hasattr(Category, key) and value.strip("'") != '':
                    query = query.filter(getattr(Category, key) == value.strip("'"))
                    
        query.filter(Category.estatus_id == 23)
        
        results = query.all()
        if not results:
            return results, 200
        
        print(f"results: {results}")
        serialized_results = [schema.dump(item) for item in results]
        print(f"serialized_results: {serialized_results}")
        
        return serialized_results, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
def create_category():
    try:
        data = request.get_json()
        print(f"data: {data}")
        schema = CategorySchema(session=db.session)
        
        # Validar los datos de entrada
        errors = schema.validate(data)
        print(f"errors: {errors}")
        if errors:
            return {"errors": errors}, 400
        
        # Crear un nuevo producto
        new_category = Category(**data)
        # deseo agregar el campo ip
        # new_product.ip = getIP()
        # new_product.created_at = datetime.now()
        
        # Guardar en la base de datos
        db.session.add(new_category)
        db.session.commit()
        
        return schema.dump(new_category), 201
    except Exception as e:
        return {"error": str(e)}, 500

def update_category(id):
    try:
        data = request.get_json()
        print(f"data: {data}")
        schema = CategorySchema(session=db.session)
        
        # Validar los datos de entrada
        errors = schema.validate(data)
        print(f"errors: {errors}")
        if errors:
            return {"errors": errors}, 400
        
        # Actualizar el producto
        category = db.session.query(Category).get(id)
        if not category:
            return {"error": "Category not found"}, 404
        
        for key, value in data.items():
            setattr(category, key, value)
        
        # Guardar en la base de datos
        db.session.commit()
        
        return schema.dump(category), 200
    except Exception as e:
        return {"error": str(e)}, 500
    

def delete_category(id):
    try:
        # Eliminar el producto
        category = db.session.query(Category).get(id)
        if not category:
            return {"error": "Category not found"}, 404
        
        db.session.delete(category)
        db.session.commit()
        
        return {"message": "Category deleted"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
    