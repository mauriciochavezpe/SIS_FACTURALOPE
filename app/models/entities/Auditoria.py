from app import db
# from .Auditory import Auditoria
from datetime import datetime

class Auditoria(db.Model):
    __abstract__= True
    ip = db.Column(db.String(80), nullable=True)
    createdBy = db.Column(db.String(80))
    modifiedBy = db.Column(db.String(80))
    createdAt = db.Column(db.DateTime)
    modifiedAt = db.Column(db.DateTime)