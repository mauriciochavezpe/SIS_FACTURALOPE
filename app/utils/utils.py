import logging
from typing import Optional, Dict
from num2words import num2words
from decimal import Decimal, ROUND_DOWN


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# SUNAT Response Codes Dictionary
SUNAT_CODES: Dict[str, str] = {
    "0": "Aceptado",
    "98": "Aceptado con observaciones",
    "99": "Rechazado",
    "9999": "Error en el sistema de SUNAT",
    "0011": "RUC del emisor no está habido",
    "0128": "El comprobante ya fue informado",
    "0149": "Serie y número ya informados",
    "0151": "Valor de elementos o atributos no corresponde al tipo de documento",
    "2033": "El documento modificado no existe",
    "2034": "El documento modificado está dado de baja"
}

# Document Type Constants
FACTURA = "01"
BOLETA = "03"
NOTA_CREDITO = "07"
NOTA_DEBITO = "08"

def get_sunat_response_code(response_code: str) -> Optional[str]:
    """
    Get SUNAT response description based on response code.
    
    Args:
        response_code (str): SUNAT response code
    Returns:
        str: Description of the response code or None if error
    """
    try:
        description = SUNAT_CODES.get(response_code, "No se encontró el código")
        logger.info(f"SUNAT Response: {response_code} - {description}")
        return description
    except Exception as e:
        logger.error(f"❌ Error al obtener código SUNAT: {str(e)}")
        return None


def get_sunat_response_xml(description) -> Optional[str]:
    """
    Extract text content from SUNAT XML response description.
    
    Args:
        description: XML description element
    Returns:
        str: Description text or None if error
    """
    try:
        print(f"Descripción XML: {description}")
        if description is not None:
            content = description.text
            logger.info(f"SUNAT XML Response: {content}")
            return content
        return "No se encontró la descripción"
    except Exception as e:
        logger.error(f"❌ Error al obtener descripción SUNAT: {str(e)}")
        return None

def validate_document_serie(tipo_doc: str, serie: str) -> bool:
    """
    Validate document series format based on document type.
    
    Args:
        tipo_doc (str): Document type code
        serie (str): Document series
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        serie_validations = {
            FACTURA: lambda s: s.startswith('F'),
            BOLETA: lambda s: s.startswith('B'),
            NOTA_CREDITO: lambda s: s.startswith(('FC', 'BC')),
            NOTA_DEBITO: lambda s: s.startswith(('FD', 'BD'))
        }
        
        validator = serie_validations.get(tipo_doc)
        if not validator:
            logger.warning(f"Tipo de documento no soportado: {tipo_doc}")
            return False
            
        is_valid = validator(serie)
        logger.info(f"Serie validation: {serie} for doc type {tipo_doc} - {'Valid' if is_valid else 'Invalid'}")
        return is_valid
        
    except Exception as e:
        logger.error(f"❌ Error validando serie: {str(e)}")
        return False
    


def build_note_amount_text(amount, currency="SOLES"):
    """
    Devuelve el fragmento XML <cbc:Note> con el monto en letras.
    Ejemplo: 3.54 -> <cbc:Note languageLocaleID="1000">TRES CON 54/100 SOLES</cbc:Note>
    """
    amount_decimal = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    entero = int(amount_decimal)
    decimal = int((amount_decimal - Decimal(entero)) * 100)
    monto_letras = num2words(entero, lang='es').upper()
    texto = f"{monto_letras} CON {decimal:02d}/100 {currency}"
    logger.info(f"Texto generado: {texto}")
    return texto