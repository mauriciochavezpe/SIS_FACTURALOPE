from flask import request
from app.models.entities.Category import Category
from app.schemas.category_schema import CategorySchema
from app.extension import db
from datetime import datetime
from app.utils.catalog_manager import catalog_manager
from app.utils.utils_constantes import Constantes
def get_all_categories():
    schema = CategorySchema(session=db.session, many=True)
    filter_data = request.args.to_dict()
    query = db.session.query(Category)
    try:
        if filter_data:
            for key, value in filter_data.items():
                if hasattr(Category, key) and value.strip("'") != '':
                    query = query.filter(getattr(Category, key) == value.strip("'"))
                    
        active_status_id = catalog_manager.get_id(Constantes.CATALOG_STATUS, Constantes.STATUS_ACTIVE)
        if active_status_id:
            query = query.filter(Category.id_status == active_status_id)
        
        results = query.all()
        return schema.dump(results), 200
    except Exception as e:
        return {"error": str(e)}, 500
    
def create_category():
    try:
        data = request.get_json()
        schema = CategorySchema(session=db.session)
        
        errors = schema.validate(data)
        if errors:
            return {"errors": errors}, 400
        print(request)
        new_category = Category(**data)
        new_category.createdAt = datetime.now()
        new_category.createdBy = data.get("user","SYSTEM")
        new_category.ip = request.remote_addr
        
        db.session.add(new_category)
        db.session.commit()
        
        return schema.dump(new_category), 201
    except Exception as e:
        return {"error": str(e)}, 500

def update_category(id):
    try:
        data = request.get_json()
        schema = CategorySchema(session=db.session)
        
        errors = schema.validate(data)
        if errors:
            return {"errors": errors}, 400
        
        category = db.session.query(Category).get(id)
        if not category:
            return {"error": "Category not found"}, 404
        
        for key, value in data.items():
            setattr(category, key, value)
        
        category.modifiedAt = datetime.now()
        category.modifiedBy = data.get("user","SYSTEM")
        category.ip = request.remote_addr

        db.session.commit()
        
        return schema.dump(category), 200
    except Exception as e:
        return {"error": str(e)}, 500
    

def delete_category(id):
    try:
        category = db.session.query(Category).get(id)
        if not category:
            return {"error": "Category not found"}, 404
        
        db.session.delete(category)
        db.session.commit()
        
        return {"message": "Category deleted"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
    