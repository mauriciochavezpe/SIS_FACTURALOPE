from enum import Enum

class FileType(Enum):
    """Tipos de archivos permitidos para almacenamiento"""
    PNG = ('image/png', '.png')
    JPEG = ('image/jpeg', '.jpg')
    PDF = ('application/pdf', '.pdf')
    EXCEL = ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx')
    WORD = ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx')
    
    def __init__(self, mime_type, extension):
        self.mime_type = mime_type
        self.extension = extension
    
    @classmethod
    def get_allowed_extensions(cls):
        """Retorna lista de extensiones permitidas"""
        return [member.extension.strip('.') for member in cls]
    
    @classmethod
    def get_mime_types(cls):
        """Retorna lista de tipos MIME permitidos"""
        return [member.mime_type for member in cls]
    
    @classmethod
    def is_valid_file(cls, filename, mime_type):
        """Valida si el archivo es de un tipo permitido"""
        extension = '.' + filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return any(
            extension == member.extension and mime_type == member.mime_type 
            for member in cls
        )