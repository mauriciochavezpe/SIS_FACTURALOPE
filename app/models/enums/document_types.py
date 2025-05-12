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
        
    @classmethod
    def validate_document(cls, doc_type_code: str, doc_number: str) -> bool:
        """Valida el número de documento según el tipo"""
        doc_type = cls.get_by_code(doc_type_code)
        if not doc_type:
            return False
        
        if doc_type == cls.DNI:
            return len(doc_number) == 8 and doc_number.isdigit()
        elif doc_type == cls.RUC:
            return len(doc_number) == 11 and doc_number.isdigit()
        elif doc_type == cls.CE:
            return 8 <= len(doc_number) <= 12
        elif doc_type == cls.PASSPORT:
            return 6 <= len(doc_number) <= 12
        elif doc_type == cls.CDI:
            return True  # Asume válido, puedes refinar
        return False