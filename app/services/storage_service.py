from app.models.enums.file_types import FileType
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.entities.Storage import Storage
from app.schemas.storage_schema import StorageSchema

#importar request
from flask import request

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(FileType.get_allowed_extensions())

def create_storage():
    try:
        if 'file' not in request.files:
            return {"error": "No file provided"}, 400
            
        file = request.files['file']
        if file.filename == '':
            return {"error": "No file selected"}, 400
            
        if not FileType.is_valid_file(file.filename, file.content_type):
            return {
                "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            }, 400
            
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        storage = Storage(
            file_name=filename,
            file_path=file_path,
            file_type=file.content_type,
            file_size=os.path.getsize(file_path),
            eid_status=1  # Active status
        )
        
        db.session.add(storage)
        db.session.commit()
        
        schema = StorageSchema(session=db.session)
        return schema.dump(storage), 201
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        db.session.rollback()
        return {"error": str(e)}, 500

def update_storage(id):
    try:
        storage = Storage.query.get(id)
        if not storage:
            return {"error": "Storage not found"}, 404
            
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                # Delete old file
                if os.path.exists(storage.file_path):
                    os.remove(storage.file_path)
                
                # Save new file
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                storage.file_name = filename
                storage.file_path = file_path
                storage.file_type = file.content_type
                storage.file_size = os.path.getsize(file_path)
        
        db.session.commit()
        schema = StorageSchema(session=db.session)
        return schema.dump(storage), 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def delete_storage(id):
    try:
        storage = Storage.query.get(id)
        if not storage:
            return {"error": "Storage not found"}, 404
            
        # Delete physical file
        if os.path.exists(storage.file_path):
            os.remove(storage.file_path)
            
        db.session.delete(storage)
        db.session.commit()
        return {"message": "Storage deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def get_all_storage():
    try:
        schema = StorageSchema(session=db.session)
        storages = db.session.query(Storage).all()
        return schema.dump(storages, many=True), 200
    except Exception as e:
        return {"error": str(e)}, 500