from app.models.entities.Serie import Serie



def obtener_siguiente_numero(tipo_comprobante, serie):
    registro = Serie.query.filter_by(tipo_comprobante=tipo_comprobante, serie=serie).first()
    if not registro:
        raise Exception(f"No existe configuración de serie {serie} para tipo {tipo_comprobante}")
    
    correlativo = registro.ultimo_correlativo + 1
    numero = f"{serie}-{correlativo:08d}"  # ejemplo: F001-00000001
    return numero, correlativo
