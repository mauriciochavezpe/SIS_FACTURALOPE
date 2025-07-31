from app.models.entities.Serie import Serie
from app.extension import db
from flask import request
from datetime import datetime

def get_all_series():
    try:
        series = Serie.query.all()
        return [s.to_dict() for s in series], 200
    except Exception as e:
        return {"error": str(e)}, 500

def create_serie():
    try:
        data = request.get_json()
        
        new_serie = Serie(
            tipo_comprobante=data['tipo_comprobante'],
            serie=data['serie'],
            ultimo_correlativo=data.get('ultimo_correlativo', 0),
            createdAt=datetime.now(),
            createdBy="system",
            ip=request.remote_addr
        )
        
        db.session.add(new_serie)
        db.session.commit()
        
        return new_serie.to_dict(), 201
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def update_serie(id):
    try:
        data = request.get_json()
        serie = Serie.query.get(id)
        
        if not serie:
            return {"error": "Serie not found"}, 404
            
        serie.tipo_comprobante = data.get('tipo_comprobante', serie.tipo_comprobante)
        serie.serie = data.get('serie', serie.serie)
        serie.ultimo_correlativo = data.get('ultimo_correlativo', serie.ultimo_correlativo)
        serie.modifiedAt = datetime.now()
        serie.modifiedBy = "system"
        serie.ip = request.remote_addr
        
        db.session.commit()
        
        return serie.to_dict(), 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def delete_serie(id):
    try:
        serie = Serie.query.get(id)
        if not serie:
            return {"error": "Serie not found"}, 404
            
        db.session.delete(serie)
        db.session.commit()
        
        return {"message": "Serie deleted"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def get_last_number(tipo_comprobante, serie):
    registro = Serie.query.filter_by(tipo_comprobante=tipo_comprobante, serie=serie).first()
    
    if not registro:
        registro = Serie(
            tipo_comprobante=tipo_comprobante,
            serie=serie,
            ultimo_correlativo=1,
            createdAt=datetime.now(),
            createdBy="system",
            ip=request.remote_addr
        )
        db.session.add(registro)
        db.session.commit()
        correlativo = 1
    else:
        registro.ultimo_correlativo += 1
        registro.modifiedAt = datetime.now()
        registro.modifiedBy = "system"
        registro.ip = request.remote_addr
        db.session.commit()
        correlativo = registro.ultimo_correlativo

    numero = f"{serie}-{correlativo:08d}"
    return {"serie": numero, "correlativo":correlativo}
