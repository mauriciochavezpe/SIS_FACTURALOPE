from app.models.entities.Serie import Serie

from app import db  # asegúrate de importar tu instancia de db
def get_last_number(tipo_comprobante, serie):
    from app import db

    # Busca la serie en la base de datos
    registro = Serie.query.filter_by(tipo_comprobante=tipo_comprobante, serie=serie).first()
    
    # Si no existe, la crea con correlativo 1
    if not registro:
        registro = Serie(
            tipo_comprobante=tipo_comprobante,
            serie=serie,
            ultimo_correlativo=1
        )
        db.session.add(registro)
        db.session.commit()
        correlativo = 1
    else:
        # Incrementa el correlativo
        registro.ultimo_correlativo += 1
        db.session.commit()
        correlativo = registro.ultimo_correlativo

    # Genera el número en formato F001-00000001
    numero = f"{serie}-{correlativo:08d}"
    return {"serie": numero, "correlativo":correlativo}
