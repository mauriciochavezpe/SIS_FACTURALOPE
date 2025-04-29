
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from app import schemas, models
# from app.database import get_db

# from app.services import category_service
# category_router = APIRouter()
# @category_router.post("/category/", response_model=schemas.CategoryResponse)
# def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
#     try:
#         return category_service.create_category(category, db)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

from flask import Blueprint, jsonify, request
from app.services.category_service import create_category, get_all_categories,update_category,delete_category
category_router = Blueprint('category_router', __name__)

@category_router.route('/', methods=['POST'])
def create_category_route():
    try:
        category_data = request.get_json()
        category, status = create_category(category_data)
        return jsonify(category), status
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@category_router.route('/', methods=['GET'])
def get_all_categories_route():
    try:
        categories,status = get_all_categories()
        return jsonify(categories),status
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @category_router.route('/<int:category_id>', methods=['GET'])
# def get_category_by_id(category_id):
#     try:
#         category,status = get_category_by_id(category_id)
#         return jsonify(category),status
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@category_router.router('/<int:category_id>', methods=['PUT'])
def update_category_route(category_id):
    try:
        category_data = request.get_json()
        category,status = update_category(category_id,category_data)
        return jsonify(category),status
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@category_router.route('/<int:category_id>', methods=['DELETE'])
def delete_category_route(category_id):
    try:
        status = delete_category(category_id)
        return jsonify({'message': 'Category deleted successfully'}), status
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500