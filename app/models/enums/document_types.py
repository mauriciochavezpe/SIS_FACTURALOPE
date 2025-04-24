from enum import Enum

class DocumentType(Enum):
    """
    Tipos de documentos según SUNAT
    Ref: https://cpe.sunat.gob.pe/informacion_general/tipos_sistemas
    """
    DNI = ('1', 'DNI - Documento Nacional de Identidad')
    CE = ('4', 'CE - Carnet de Extranjería')
    RUC = ('6', 'RUC - Registro Único de Contribuyentes')
    PASSPORT = ('7', 'PASAPORTE')
    CDI = ('A', 'CDI - Cédula Diplomática de Identidad')
    
    def __init__(self, code, description):
        self.code = code
        self.description = description
    
    @classmethod
    def get_by_code(cls, code):
        for doc_type in cls:
            if doc_type.code == code:
                return doc_type
        return None
    
    @classmethod
    def to_dict(cls):
        return {doc_type.name: {
            'code': doc_type.code,
            'description': doc_type.description
        } for doc_type in cls}