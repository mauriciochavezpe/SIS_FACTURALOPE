from zeep import Client, Transport
from zeep.wsse.username import UsernameToken    
import logging
from zeep.settings import Settings
from requests.adapters import HTTPAdapter
from datetime import datetime
from dotenv import load_dotenv
import requests
import base64
import time
import os
import zipfile
import io

from app.utils.xml_utils.file_utils import FileUtils
from .utils import get_sunat_response_code, get_sunat_response_xml
from app.config.certificado import firmar_xml_con_placeholder
from enum import Enum
from xml.etree import ElementTree as ET
from app.services.serie_services import get_last_number
from app.services.customer_service import get_all_customers_by_ruc
# from app.services.invoice_service import crear_factura_standard
# Configurar logging para debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def descargar_wsdl_local(url, ruta_local="app/wsdl/billService_beta.wsdl"):
    """Descarga el WSDL y lo guarda localmente para evitar problemas de conexión"""
    try:
        import requests
        from pathlib import Path
        
        # Crear directorio si no existe
        Path(ruta_local).parent.mkdir(parents=True, exist_ok=True)
        
        # Descargar WSDL
        response = requests.get(url, timeout=30, verify=True)
        response.raise_for_status()
        
        # Validar que sea XML válido
        import xml.etree.ElementTree as ET
        try:
            ET.fromstring(response.content)
        except ET.ParseError as e:
            return False, f"WSDL no es XML válido: {e}"
        
        # Guardar archivo
        with open(ruta_local, 'wb') as f:
            f.write(response.content)
            
        logger.info(f"WSDL descargado exitosamente en: {ruta_local}")
        return True, ruta_local
        
    except Exception as e:
        logger.error(f"Error descargando WSDL: {e}")
        return False, str(e)

def download_file(url, dest, auth_header):
    try:
        headers = {
            "Authorization": auth_header
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        with open(dest, "wb") as f:
            f.write(response.content)
        print(f"Archivo descargado: {dest}")
    except Exception as e:
        print(f"Error al descargar el archivo {url}: {e}")
        raise

def download_wsdl_files():
    user_name = os.getenv("SUNAT_USUARIO_DUMMY")
    password = os.getenv("SUNAT_PASS_DUMMY")
    auth = "Basic " + base64.b64encode(f"{user_name}:{password}".encode()).decode()

    base_url = os.getenv("sunat_beta") # reemplaza esto por la real

    files = [
        {"url": f"{base_url}/billService?wsdl", "dest": "./app/wsdl/billService.wsdl"},
        {"url": f"{base_url}/billService?ns1.wsdl", "dest": "./app/wsdl/billService_ns1.wsdl"},
        {"url": f"{base_url}/billService.xsd2.xsd", "dest": "./app/wsdl/billService.xsd2.xsd"},
    ]

    for file in files:
        download_file(file["url"], file["dest"], auth)
        time.sleep(0.5)

 
