from flask import request
from app.models.entities.User import User
from app.schemas.user_schema import UserSchema
from app.extension import db
from datetime import datetime

def get_all_users():
    schema = UserSchema(session=db.session, many=True)
    filter_data = request.args.to_dict()
    query = db.session.query(User)
    try:
        if filter_data:
            for key, value in filter_data.items():
                if hasattr(User, key) and value.strip("'") != '':
                    query = query.filter(getattr(User, key) == value.strip("'"))
                 
        query = query.filter(User.id_status == 23)
        
        results = query.all()
        return schema.dump(results), 200
    except Exception as e:
        return {"error": str(e)}, 500

def create_user():
    try:
        user_data = request.get_json()
        password = user_data.pop('password', None)
        if not password:
            return {"error": "Password is required"}, 400

        schema = UserSchema(session=db.session, exclude=['password_hash'])
        user = schema.load(user_data, session=db.session)
        user.set_password(password)
        user.id_status = 1
        user.createdAt = datetime.now()
        user.createdBy = data.get("user","SYSTEM")
        user.ip = request.remote_addr

        db.session.add(user)
        db.session.commit()
        
        return schema.dump(user), 201
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def get_user_by_id(user_id):
    try:
        schema = UserSchema(session=db.session)
        user = db.session.query(User).filter_by(id=user_id).first()
        if user:
            return schema.dump(user), 200
        else:
            return {"error": "User not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

def update_user(user_id):
    try:
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return {"error": "User not found"}, 404
            
        user_data = request.get_json()
        
        if 'password' in user_data:
            password = user_data.pop('password')
            user.set_password(password)

        schema = UserSchema(session=db.session, exclude=['password_hash'])
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.modifiedAt = datetime.now()
        user.modifiedBy = data.get("user","SYSTEM")
        user.ip = request.remote_addr
                
        db.session.commit()
        
        return schema.dump(user), 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def login_user():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {"error": "Email and password are required"}, 400

        user = db.session.query(User).filter_by(email=email).first()

        if user and user.check_password(password):
            schema = UserSchema(session=db.session)
            return schema.dump(user), 200
        else:
            return {"error": "Invalid credentials"}, 401
    except Exception as e:
        return {"error": str(e)}, 500

def logout_user():
    try:
        return {"message": "Logged out successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
