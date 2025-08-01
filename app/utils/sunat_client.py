"""
Este módulo se encarga exclusivamente de la comunicación con el servicio de SUNAT.
Orquesta la obtención de datos, la generación del XML, la firma
y el envío del documento electrónico.
"""

import io
import os
import zipfile
from typing import Any, Dict
from xml.etree import ElementTree as ET

from zeep import Client
from zeep.wsse.username import UsernameToken

from app.config.certificado import firmar_xml_con_placeholder
from app.services.customer_service import get_all_customers_by_ruc
from app.services.invoice_service import get_invoice_by_serie_num
from app.services.master_data_service import get_master_data_by_catalog
from app.utils.utils import get_sunat_response_code, get_sunat_response_xml
from app.utils.xml_generate_fragments import (
     complete_data_xml)
from app.utils.xml_utils.file_utils import FileUtils
from app.utils.utils_constantes import Constantes
class SunatClientError(Exception):
    """Excepción base para errores relacionados con el cliente de SUNAT."""
    pass


def send_invoice_data_to_sunat(data: Dict[str, Any]):
    """
    Orquesta el proceso completo de envío de un documento a SUNAT a partir de datos.
    """
    try:
        # 1. Obtener datos adicionales necesarios para el XML
        document_type = data.get("document_type")
        sunat_ruc = os.getenv("SUNAT_RUC")
        if not sunat_ruc:
            raise SunatClientError(
                "La variable de entorno SUNAT_RUC no está configurada.")

        rucs = [sunat_ruc, data.get("ruc_cliente")]
        payload_customers, status_cust = get_all_customers_by_ruc(rucs)
        if status_cust != 200:
            raise SunatClientError(
                f"Error al obtener datos de clientes: {payload_customers}")
        invoice_relative, catalog_07 = None, None

        ## obtenemos la factura relativa
        if document_type in ["07", "08"]:
            invoice_relative, status_inv = get_invoice_by_serie_num(
                data.get("relative_document"))
            
            if status_inv != 200:
                raise SunatClientError(
                    f"Error al obtener factura relacionada: {invoice_relative}")

        if document_type in ["01", "03"]:
            afecto_tributo = data.get("afecto_tributo")
            catalog_07, status_cat = get_master_data_by_catalog(
                Constantes.CATALOG_07_IGV, afecto_tributo)
            if status_cat != 200:
                raise SunatClientError(
                    f"Error al obtener catálogo {Constantes.CATALOG_07_IGV}: {catalog_07}")
        # print(f"Datos obtenidos: {payload_customers}, {catalog_07}, {invoice_relative}")
        # 2. Generar el XML
        xml_string, serie_number = complete_data_xml(
            data=data,
            payload_customers=payload_customers,
            catalog_07=catalog_07,
            invoice_relative=invoice_relative
        )
        # 3. Firmar y empaquetar
        xml_firmado = firmar_xml_con_placeholder(xml_string)
        name_file = f"{sunat_ruc}-{document_type}-{serie_number}"
        zip_base64 = _create_zip_for_sunat(xml_firmado, name_file)

        # 4. Enviar a SUNAT y procesar respuesta
        cdr_response = _send_bill_to_sunat_ws(f"{name_file}.zip", zip_base64)
        return cdr_response

    except (ValueError, SunatClientError) as e:
        # Captura errores conocidos y los re-lanza para el orquestador
        raise SunatClientError(f"Error en el proceso de envío a SUNAT: {e}")


def _create_zip_for_sunat(xml_content: str, name_file: str) -> str:
    """Crea el archivo ZIP en base64 a partir del XML firmado."""
    try:
        file_utils = FileUtils("assets")
        payload_zip = file_utils.create_zip(
            xml_content, f"{name_file}.xml", f"{name_file}.zip")

        if not payload_zip or 'content_base64' not in payload_zip:
            raise SunatClientError("Error al crear el archivo ZIP.")
        return payload_zip['content_base64']
    except Exception as e:
        raise SunatClientError(f"Fallo en la creación del ZIP: {e}")


def _send_bill_to_sunat_ws(nombre_zip: str, zip_base64: str) -> Dict[str, Any]:
    """Se conecta al Web Service de SUNAT y envía el archivo ZIP."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        wsdl_path = os.path.join(
            current_dir, "..", "wsdl", "billService.wsdl")
        wsdl_path = os.path.abspath(wsdl_path)

        wsse = UsernameToken(os.getenv("SUNAT_USUARIO_DUMMY"),
                             os.getenv("SUNAT_PASS_DUMMY"))
        client = Client(wsdl=wsdl_path, wsse=wsse)

        print(f"📤 Enviando comprobante {nombre_zip} a SUNAT...")
        payload = client.service.sendBill(
            fileName=nombre_zip, contentFile=zip_base64)

        result = _unzip_and_process_cdr(payload)
        print("✅ Envío correcto. SUNAT respondió con CDR.")
        return result

    except Exception as e:
        raise SunatClientError(f"Error en la comunicación con SUNAT WS: {e}")


def _unzip_and_process_cdr(zip_bytes: bytes) -> Dict[str, Any]:
    """Descomprime y procesa el archivo CDR de respuesta de SUNAT."""
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
            nombre_xml_cdr = zip_file.namelist()[1]
            xml_bytes_cdr = zip_file.read(nombre_xml_cdr)

            file_utils = FileUtils("CDR")
            file_utils.create_xml(xml_bytes_cdr.decode("utf-8"), nombre_xml_cdr)

            return _read_xml_cdr(xml_bytes_cdr, nombre_xml_cdr)
    except (zipfile.BadZipFile, IndexError) as e:
        raise SunatClientError(f"Error al procesar el CDR de SUNAT: {e}")


def _read_xml_cdr(xml_bytes: bytes, name: str) -> Dict[str, Any]:
    """Parsea el XML del CDR para extraer la respuesta de SUNAT."""
    try:
        root = ET.fromstring(xml_bytes)
        ns = {
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        }
        response_code_elem = root.find(".//cbc:ResponseCode", ns)
        description_elem = root.find(".//cbc:Description", ns)

        response_code = response_code_elem.text if response_code_elem is not None else ""
        description = description_elem.text if description_elem is not None else ""
        print(f"📄 CDR recibido: {response_code} - {description}")
        return {
            "codigo_estado": response_code,
            "estado_descripcion": get_sunat_response_code(response_code),
            "mensaje": description,
            "nombre_xml": name,
            "contenido_xml": xml_bytes.decode("utf-8"),
        }
    except ET.ParseError as e:
        raise SunatClientError(f"Error al leer el CDR XML: {e}")
