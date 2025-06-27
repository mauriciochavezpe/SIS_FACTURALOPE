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
from requests import Session
from .generar_xml import create_xml, create_zip,generar_xml
from .utils import get_sunat_response_code, get_sunat_response_xml
from app.config.certificado import firmar_xml_con_placeholder
from enum import Enum
from xml.etree import ElementTree as ET
from app.services.serie_services import get_last_number
from app import db
from app.services.invoice_service import crear_factura_standard
# Configurar logging para debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def conexion_sunat(path):
    try:
        # Validar que el archivo existe
        if not os.path.exists(path):
            return {"error": f"Archivo no encontrado: {path}"}, 404
        
        # Leer archivo ZIP
        with open(path, 'rb') as f:
            contenido_zip = base64.b64encode(f.read()).decode('utf-8')
        
       

        
        # print("zip_content", zip_content)
        # Validar que el archivo no esté vacío
        if not contenido_zip:
            return {"error": "El archivo ZIP está vacío"}, 400

        file_name = os.path.basename(path)
        logger.info(f"Procesando archivo: {file_name}")

        # Validar URL WSDL
        url_sunat = os.getenv("sunat_qas")
        print("url_sunat",url_sunat)
        # if not url_sunat:
        #     url_sunat = "app/wsdl/billService_beta.wsdl"

        base_dir = os.path.dirname(os.path.abspath(__file__))
        wsdl_path = os.path.join(base_dir,"wsdl", "billService_beta.wsdl")

        # if not os.path.exists(wsdl_path):
        #     return {"error": "WSDL local no encontrado"}, 500

        # logger.info(f"URL SUNAT: {url_sunat}")

        # Validar credenciales
        usuario = os.getenv("SUNAT_RUC") +""+ os.getenv("SUNAT_USUARIO_DUMMY") 
        password = os.getenv("SUNAT_PASS_DUMMY") 
        
        if not usuario or not password:
            return {"error": "Credenciales SUNAT no configuradas"}, 500

        data = {
            "fileName": os.path.basename(path),
            "contentFile": contenido_zip
        }
        
        string_body = build_soap_envelope(data, usuario, password)   

        session = Session()
        # Configurar sesión con timeout y reintentos
        print(f"string_body {string_body}")
        # Headers adicionales que pueden ser necesarios
        session.headers.update({
             "User-Agent": "Mozilla/5.0 (compatible; Python/Zeep)",
             "Content-Type": "text/xml; charset=utf-8",
             "SOAPAction": "urn:sendBill"
        })
        ## configurar 
        resp = session.post(url_sunat, data=string_body, timeout=60)

        print("resp",resp)        
        # Configurar transport con timeout
        # transport = Transport(session=session, timeout=60)
        # settings = Settings(strict=False, xml_huge_tree=True)
        # wsse =  UsernameToken(usuario, password)

        logger.info("minutos antes")
        # client = Client(url_sunat, transport=transport, settings=settings, wsse=wsse)
        print("HTTP status:", resp.status_code)
        print("Response headers:", resp.headers)
        print("Raw response body:\n", resp.text) 

        logger.info("Cliente SOAP creado exitosamente")
        # logger.info(f"Servicios disponibles: {[op.name for op in client.service._operations.values()]}")

        # Convertir contenido a base64 si es necesario
        # Algunos endpoints requieren base64, otros bytes directos
        try:
            print("client",resp)
            # Intentar con bytes directos primero
            # response = client.service.sendBill(file_name, contenido_zip)
        except Exception as e1:
            logger.warning(f"Falló con bytes directos, intentando con base64: {e1}")
            try:
                print("client",resp)
                # Intentar con base64
                # zip_base64 = base64.b64encode(contenido_zip).decode('utf-8')
                # response = client.service.sendBill(file_name, zip_base64)
            except Exception as e2:
                logger.error(f"Falló también con base64: {e2}")
                raise e1  # Lanzar el error original

        logger.info("Respuesta recibida de SUNAT")

        # Validar respuesta
        # if not hasattr(response, 'applicationResponse'):
        #     return {"error": "Respuesta inválida de SUNAT - sin applicationResponse"}, 500

        # # Procesar CDR
        # cdr_content = response.applicationResponse
        # if not cdr_content:
        #     return {"error": "CDR vacío en la respuesta"}, 500

        # # Guardar CDR
        # cdr_filename = f'{file_name.replace(".zip", "")}-CDR.zip'
        
        # # Si el CDR viene en base64, decodificarlo
        # if isinstance(cdr_content, str):
        #     try:
        #         cdr_content = base64.b64decode(cdr_content)
        #     except Exception:
        #         # Si no es base64 válido, usar tal como viene
        #         cdr_content = cdr_content.encode('utf-8')
        
        # with open(cdr_filename, 'wb') as f:
        #     f.write(cdr_content)

        # logger.info(f"CDR guardado como: {cdr_filename}")

        # # Información adicional de la respuesta si está disponible
        # response_info = {
        #     "message": "Envío exitoso, revisa el CDR de respuesta.",
        #     "cdr_file": cdr_filename,
        #     "original_file": file_name
        # }

        # # Agregar información adicional si está disponible en la respuesta
        # if hasattr(response, 'status'):
        #     response_info["status"] = response.status
        # if hasattr(response, 'statusMessage'):
        #     response_info["status_message"] = response.statusMessage

        # print("✅ Envío exitoso. Revisa el CDR.")
        return resp, 200

    except Exception as e:
        error_msg = f"Error al enviar a SUNAT: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(f"❌ {error_msg}")
        
        # Información más detallada del error
        error_response = {
            "error": str(e),
            "error_type": type(e).__name__,
            "file": path if 'path' in locals() else "No especificado"
        }
        
        return error_response, 500


 
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


def send_to_sunat(xml_firmado, info_xml,data, env = "qas"):
    try:
        if env == "qas":
            URL = os.getenv("sunat_qas")
        elif env == "prod":
            URL = os.getenv("sunat_prod")

        #generacion de name del file
        ruc = os.getenv("SUNAT_RUC")
        tipo_doc = "01"
        name_file = f"{ruc}-{tipo_doc}-{info_xml.get('serie')}" # Ej: 20512345678-01-F001-00000001
        nombre_xml = f"{name_file}.xml"
        nombre_zip =  f"{name_file}.zip"
        RB = "assets" # ruta_base
       
        try:
            #guardamos el file en la carpeta assets
            create_xml(xml_firmado,RB, nombre_xml)
            payload_zip, status= create_zip(xml_firmado,RB, nombre_zip)
            # print("status",status)
            if status == 200:
                zip_base64 = payload_zip['content_base64']
            else:
                raise Exception("Error al crear el ZIP")
        except Exception as e:
            return {"error": str(e)}, 500
        
       

        # BUSCAR EL WSDL LOCAL
        current_dir = os.path.dirname(os.path.abspath(__file__))  # /.../app/utils
        wsdl_path = os.path.join(current_dir, "..", "wsdl", "billService.wsdl")
        wsdl_path = os.path.abspath(wsdl_path)
        usuario = os.getenv("SUNAT_USUARIO_DUMMY")
        password = os.getenv("SUNAT_PASS_DUMMY")
        # print(f"{usuario} {password}")
        userNameToken = UsernameToken(usuario,password)
        client = Client(
        wsdl=wsdl_path,  # Asegúrate que esté en esta ruta
        wsse=userNameToken
        )

        
        # Preparar parámetros
        args = {
            'fileName': nombre_zip,
            'contentFile': zip_base64
        }
        # print("args",args)
        # Enviar a SUNAT
        try:
            print("📤 Enviando comprobante a SUNAT...")
            payload = client.service.sendBill(**args)

            result = descomprimir_cdr(payload)
            ## agregar factura a la base de datos
            # Aquí puedes agregar la lógica para guardar el resultado en tu base de datos
            create_structure_invoice = {
                                      "date": datetime.now(),
                                      "customer_id": 1,
                                      "num_invoice": f"{info_xml.get('correlativo'):08d}",
                                      "serie": info_xml.get("serie").split("-")[0],
                                      "subtotal": data.get("subtotal"),
                                      "total": data.get("monto_total"),
                                      "details": [
                                          {
                                              "product_id": 1,
                                              "quantity": 1,
                                              "unit_price": data.get("monto_total"),
                                              "discount": 0,
                                              "subtotal": data.get("subtotal"),
                                              "tax": data.get("monto_igv"),
                                              "total": data.get("monto_total")
                                          }]
                                      }
            crear_factura_standard(create_structure_invoice)

            print("✅ Enviado correctamente. SUNAT respondió con CDR.")
            return result
        except Exception as e:
            print("❌ Error al enviar a SUNAT:", str(e))
            raise
        
    except Exception as e:
        return {"error":"Error al enviar a SUNAT", "error_type": type(e).__name__, "full_error": str(e)}, 500

def descomprimir_cdr(zip_bytes):
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
            # de momento consideramos el 1 porque el otro es dummy
            nombre_xml = zip_file.namelist()[1]  # Ej: R-20512345678-01-F001-00000001.xml
            xml_bytes = zip_file.read(nombre_xml)
            data = {
                "filename": nombre_xml,
                "documento": xml_bytes
            }
            # la ruta
            current_dir = os.path.dirname(os.path.abspath(__file__))  # /.../app/utils
            carpeta_cdr = os.path.join(current_dir, "..", "CDR")
            create_xml(xml_bytes, carpeta_cdr, nombre_xml)
            create_zip(xml_bytes, carpeta_cdr, nombre_xml)

            return read_xml_cdr(xml_bytes,nombre_xml)

    except zipfile.BadZipFile as e:
        print("❌ Error al descomprimir el CDR:", str(e))
        raise
    except Exception as e:
        print("❌ Error al descomprimir el CDR:", str(e))
        raise

def read_xml_cdr(xml_bytes, name):
    try:

        # Descomprimir el ZIP en memoria
        # with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
        #     nombre_xml = zip_file.namelist()[0]  # Ej: RUC-01-F001-00000001.xml
        #     xml_bytes = zip_file.read(nombre_xml)

        # Parsear el XML
        root = ET.fromstring(xml_bytes)

        # Extraer información básica del CDR
        ns = {
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        }

        response_code = root.find(".//cbc:ResponseCode", ns)
        description = root.find(".//cbc:Description", ns)

        MESSAGE_SUNAT_RETURN = get_sunat_response_code(response_code.text)
        MENSAJE_SUNAT_XML = get_sunat_response_xml(description)

        contenido_xml = xml_bytes.decode("utf-8")

        payload = {
            "estado": MESSAGE_SUNAT_RETURN,
            "mensaje": MENSAJE_SUNAT_XML,
            "nombre_xml": name,
            "contenido_xml": contenido_xml,
        }
        return payload
    except Exception as e:
        print(f"❌ Error al leer la fn read_xml_cdr: {e}")
        return {"message": str(e)}, 500

def validar_ruc(ruc):
    try:
        """
        Valida el RUC peruano.
        
        Args:
            ruc (str): RUC a validar.
            
        Returns:
            bool: True si el RUC es válido, False en caso contrario.
        """
        url_request = os.getenv("VALIDAR_RUC_SUNAT")
        url_request = url_request.replace("XXXXX", ruc)
    
        response = requests.get(url_request, timeout=10)
        payload = response.json()
        # print("payload",payload)
        if("error" in payload):
            print("❌ Error al validar RUC:", payload["error"])
            # return {"error": payload["error"]}, 500
            raise ValueError(payload["error"])
        else:
            cliente = payload.get("lista", [])
            # quitar los espacios en blanco
            if cliente and isinstance(cliente[0], dict):
                cliente[0] = {k: v.strip() if isinstance(v, str) else v for k, v in cliente[0].items()}
            return cliente
    # return response
    except Exception as e:
        print(f"❌ Error al validar RUC: {e}")
        return {"error": str(e)}, 500

def agregar_datos_ruc_generico(xml_string, ruc, sufijo=""):
    """
    Reemplaza los placeholders de datos de RUC en el XML.
    Si sufijo es '', reemplaza los del emisor; si es '1', los del cliente.
    """
    try:
        payload = validar_ruc(ruc)
        if not payload or not isinstance(payload, list) or len(payload) == 0:
            return {"error": "RUC no encontrado o inválido"}, 404
        item = payload[0]
        # Ajustar los nombres de los campos según el payload real
        campos = [
            ("@razon_social" + sufijo,  item.get("apenomdenunciado", "")),
            ("@direccion" + sufijo,  item.get("direstablecimiento", "")),
            ("@distrito" + sufijo,  item.get("desdistrito", "")),
            ("@provincia" + sufijo, item.get("desprovincia", "")),
            ("@departamento" + sufijo, item.get("desdepartamento", "")),
        ]
        for placeholder, valor in campos:
            xml_string = xml_string.replace(placeholder, valor if valor is not None else "")
        xml_string = xml_string.replace("@ruc" + sufijo, ruc)
        return xml_string
    except Exception as e:
        print(f"❌ Error al agregar datos del RUC: {e}")
        return {"error": str(e)}, 500

# Compatibilidad con nombres anteriores
def agregar_datos_ruc(xml_string, ruc):
    return agregar_datos_ruc_generico(xml_string, ruc, sufijo="")

def agregar_datos_ruc_cliente(xml_string, ruc):
    return agregar_datos_ruc_generico(xml_string, ruc, sufijo="1")
    
def complete_data_xml(data):
    load_dotenv()
    """
    Completa el XML con los datos proporcionados.
    
    Args:
        xml_string (str): XML con placeholders.
        data (dict): Datos a completar en el XML.
        
    Returns:
        str: XML completado.
    """
    try:
        xml_string = generar_xml()  # Aquí se obtiene el XML con placeholders
        xml_string = agregar_datos_ruc_cliente(xml_string,data.get("ruc_cliente"))  # Agregar datos del RUC emisor
        xml_string = agregar_datos_ruc(xml_string,os.getenv("SUNAT_RUC"))  # Agregar datos del RUC cliente
        xml_string = xml_string.replace("@fecha", datetime.now().strftime("%Y-%m-%d"))
        try:
           serie_number = get_last_number(data.get("tipo_documento"), data.get("documento").split("-")[0])
        except Exception as e:
            raise ValueError(f"Error al obtener el tipo de documento. Asegúrate de que el campo 'documento' esté presente en los datos. {e}")
        xml_string = xml_string.replace("@serie", serie_number.get("serie"))
        xml_string = xml_string.replace("@tipo_moneda", "PEN")
        xml_string = xml_string.replace("@tipo", "01")
        xml_string = xml_string.replace("@monto_total", data.get("monto_total"))
        xml_string = xml_string.replace("@monto_igv", data.get("monto_igv"))
        xml_string = xml_string.replace("@porcentaje_igv", data.get("porcentaje_igv"))
        xml_string = xml_string.replace("@monto", data.get("monto_total"))
        xml_string = xml_string.replace("@descripcion", data.get("descripcion"))
        xml_string = xml_string.replace("@precio", data.get("monto_total"))
        xml_string = xml_string.replace("@subtotal", data.get("subtotal"))
        xml_string = xml_string.replace("@cantidad", data.get("cantidad"))
        xml_string = firmar_xml_con_placeholder(xml_string) # Firmar el XML
        return xml_string, serie_number
        
    except Exception as e:
        print(f"❌ Error al completar el XML: {e}")
        return {"error": str(e)}, 500