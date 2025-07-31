from flask import jsonify, request
from app.models.entities.User import User
from datetime import datetime
# from app.utils.utils import getIP
from app.schemas.user_schema import UserSchema
from app.extension import db

def get_all_users():
    schema = UserSchema(session=db.session)
    filter = request.args.to_dict()
    query = db.session.query(User)
    try:
        if filter:
            for key, value in filter.items():
                if hasattr(User, key) and value.strip("'") != '':
                    query = query.filter(getattr(User, key) == value.strip("'"))
                 
        query.filter(User.id_status == 23)
        
        results = query.all()
        if not results:
            return results, 200
        
        return schema.dump(results, many=True), 200
        # return jsonify([item.to_dict() for item in results]), 200
    except Exception as e:
        return {"error": str(e)}, 500

def create_user():
    try:
        user_data = request.get_json()
        password = user_data.pop('password_hash', None)
        if not password:
            return {"error": "Password is required"}, 400

        # Exclude password_hash from schema loading
        schema = UserSchema(session=db.session, exclude=['password_hash'])
        user = schema.load(user_data, session=db.session)
        user.id_status = 1
        user.set_password(password)

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

        # Exclude password_hash from schema loading
        schema = UserSchema(session=db.session, exclude=['password_hash'])
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
                
        db.session.commit()
        
        return schema.dump(user), 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

#validar inicio de sesion
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
        # Implement logout logic here (e.g., invalidate JWT token)
        return {"message": "Logged out successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500