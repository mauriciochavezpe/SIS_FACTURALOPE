from flask import jsonify, request
from app.models.User import User
from datetime import datetime
# from app.utils.utils import getIP
from app.schemas.user_schema import UserSchema
from app.extension import db

def get_all_users():
    schema = UserSchema(session=db.session)
    filter = request.args.to_dict()
    query = db.session.query(User)
    print(f"filter: {filter}")  
    try:
        
        if filter:
            for key, value in filter.items():
                if hasattr(User, key) and value.strip("'") != '':
                    query = query.filter(getattr(User, key) == value.strip("'"))
                    
        query.filter(User.id_status == 23)
        
        results = query.all()
        print(f"results: {results}")
        return jsonify([schema.dump(item) for item in results]), 200
        # return jsonify([item.to_dict() for item in results]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

