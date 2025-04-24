from enum import Enum

class InvoiceType(Enum):
    """
    Tipos de Comprobantes de Pago Electrónicos según SUNAT
    Ref: https://cpe.sunat.gob.pe/node/88
    """
    FACTURA = ('01', 'FACTURA ELECTRÓNICA')
    BOLETA = ('03', 'BOLETA DE VENTA ELECTRÓNICA')
    NOTA_CREDITO = ('07', 'NOTA DE CRÉDITO ELECTRÓNICA')
    NOTA_DEBITO = ('08', 'NOTA DE DÉBITO ELECTRÓNICA')
    GUIA_REMISION = ('09', 'GUÍA DE REMISIÓN ELECTRÓNICA')
    COMPROBANTE_RETENCION = ('20', 'COMPROBANTE DE RETENCIÓN ELECTRÓNICA')
    COMPROBANTE_PERCEPCION = ('40', 'COMPROBANTE DE PERCEPCIÓN ELECTRÓNICA')
    
    def __init__(self, code, description):
        self.code = code
        self.description = description
    
    @classmethod
    def get_by_code(cls, code):
        """Obtener tipo de documento por código"""
        for doc_type in cls:
            if doc_type.code == code:
                return doc_type
        return None
    
    @classmethod
    def to_dict(cls):
        """Convertir enum a diccionario para APIs"""
        return {doc_type.name: {
            'code': doc_type.code,
            'description': doc_type.description
        } for doc_type in cls}
    
    @classmethod
    def get_valid_series(cls, doc_type):
        """Obtener series válidas por tipo de documento"""
        series_map = {
            'FACTURA': ['F'],
            'BOLETA': ['B'],
            'NOTA_CREDITO': ['FC', 'BC'],  # FC para facturas, BC para boletas
            'NOTA_DEBITO': ['FD', 'BD']    # FD para facturas, BD para boletas
        }
        return series_map.get(doc_type.name, [])