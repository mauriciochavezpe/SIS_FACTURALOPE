from app import db

from app.models.Auditoria import Auditoria

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    id_status = db.Column(db.Integer, nullable=False)
    # is_client = db.Column(db.Boolean, default=False)
   