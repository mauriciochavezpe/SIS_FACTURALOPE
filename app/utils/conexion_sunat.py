import base64
from zeep import Client, Transport
from zeep.wsse.username import UsernameToken    
import logging
from zeep.settings import Settings
from requests.adapters import HTTPAdapter
from datetime import datetime
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
from dotenv import load_dotenv

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


def conexion_sunat_mejorada(path):
    """
    Conexión para envío de comprobantes a SUNAT Beta o Producción
    Args:
        path (str): Ruta del archivo .zip firmado a enviar
    """
    try:
        # 1. VALIDACIÓN DE ARCHIVO ZIP
        if not os.path.exists(path):
            return {"error": f"Archivo no encontrado: {path}"}, 404

        # leer el zip en base64
        with open(path, 'rb') as f:
            zip_content = f.read()

        # zip_base64 = base64.b64encode(zip_content).decode('utf-8')

        if not zip_content:
            return {"error": "El archivo ZIP está vacío"}, 400

        file_name = os.path.basename(path)
        logger.info(f"📦 Procesando archivo: {file_name}")

        # 2. DETERMINAR RUTA WSDL
        wsdl_url = ""#os.getenv("sunat_qas")  # Puede ser URL o vacío
        if not wsdl_url or not wsdl_url.startswith("http"):
            base_path = os.path.dirname(os.path.abspath(__file__))
            wsdl_url = os.path.normpath(os.path.join(base_path, "..", "wsdl", "billService.wsdl"))

        logger.info(f"🌐 WSDL a usar: {wsdl_url}")

        # 3. CREDENCIALES SUNAT
        ruc = os.getenv("SUNAT_RUC")
        usuario = os.getenv("SUNAT_USUARIO_SECUNDARIO")
        password = os.getenv("SUNAT_PASS_SECUNDARIO")

        if not all([ruc, usuario, password]):
            return {
                "error": "Credenciales incompletas para SUNAT",
                "requeridas": ["SUNAT_RUC", "SUNAT_USUARIO_SECUNDARIO", "SUNAT_PASS_SECUNDARIO"],
                "encontradas": {
                    "SUNAT_RUC": bool(ruc),
                    "SUNAT_USUARIO_SECUNDARIO": bool(usuario),
                    "SUNAT_PASS_SECUNDARIO": bool(password)
                }
            }, 500

        usuario_completo = f"{ruc}{usuario}"
        logger.info(f"👤 Usuario: {usuario_completo}")

        # 4. CONFIGURAR SESIÓN HTTP CON RETRY
        session = Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=3,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.auth = HTTPBasicAuth(usuario_completo, password)
        session.headers.update({
            'Content-Type': 'text/xml; charset=utf-8',
            'User-Agent': 'SUNAT-Client-Python/1.0',
            'Accept': 'text/xml, application/soap+xml'
        })

        transport = Transport(session=session, timeout=120, operation_timeout=120)

        # 5. CONFIGURAR CLIENTE SOAP
        settings = Settings(strict=False, xml_huge_tree=True)
        try:
            client = Client(wsdl=wsdl_url, transport=transport, settings=settings)
            logger.info("✅ Cliente SOAP creado correctamente.")
        except Exception as e:
            return {
                "error": "No se pudo cargar el WSDL correctamente",
                "detalle": str(e)
            }, 500

        # 6. PREPARAR ARCHIVO
        zip_base64 = base64.b64encode(zip_content).decode("utf-8")

        # 7. INTENTAR ENVÍO A SUNAT
        try:
            logger.info("📤 Enviando documento a SUNAT...")
            if hasattr(client.service, "sendBill"):
                response = client.service.sendBill(file_name, zip_base64)
            else:
                return {
                    "error": "El método sendBill no está disponible en el servicio",
                    "wsdl_usado": wsdl_url
                }, 500

        except Exception as e:
            logger.error(f"❌ Error en el envío a SUNAT: {e}")
            return {
                "error": f"Error enviando a SUNAT: {str(e)}",
                "sugerencias": [
                    "Revisa que el XML firmado sea correcto",
                    "Verifica el RUC y las credenciales",
                    "Prueba usando WSDL local"
                ]
            }, 500

        # 8. PROCESAR RESPUESTA
        if not hasattr(response, 'applicationResponse'):
            return {"error": "SUNAT no devolvió applicationResponse"}, 500

        cdr_zip = response.applicationResponse
        if isinstance(cdr_zip, str):
            cdr_zip = base64.b64decode(cdr_zip)
        elif isinstance(cdr_zip, bytes):
            pass
        else:
            return {"error": "CDR devuelto en formato desconocido"}, 500

        cdr_filename = f"cdr/R-{file_name}"
        os.makedirs("cdr", exist_ok=True)
        with open(cdr_filename, "wb") as f:
            f.write(cdr_zip)

        logger.info(f"📄 CDR guardado como: {cdr_filename}")

        return {
            "estado": "enviado",
            "cdr_file": cdr_filename,
            "original_file": file_name,
            "message": "✅ Envío exitoso a SUNAT. Revisa el CDR."
        }, 200

    except Exception as e:
        logger.error(f"❌ Error general conectando a SUNAT: {e}", exc_info=True)
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "file": path,
            "sugerencias": [
                "Verifica la conexión a internet",
                "Revisa el WSDL y credenciales",
                "Asegúrate que el archivo ZIP no esté dañado"
            ]
        }, 500



def procesar_respuesta_sunat(response, file_name):
    """Procesa la respuesta de SUNAT y extrae el CDR"""
    try:
        # Diferentes estructuras de respuesta según el servicio
        cdr_content = None
        status_code = None
        status_message = None
        
        # Intentar diferentes atributos de respuesta
        if hasattr(response, 'applicationResponse'):
            cdr_content = response.applicationResponse
        elif hasattr(response, 'ApplicationResponse'):
            cdr_content = response.ApplicationResponse
        elif hasattr(response, 'cdr'):
            cdr_content = response.cdr
        elif hasattr(response, 'zipFile'):
            cdr_content = response.zipFile
        
        # Obtener códigos de estado si están disponibles
        if hasattr(response, 'statusCode'):
            status_code = response.statusCode
        elif hasattr(response, 'StatusCode'):
            status_code = response.StatusCode
            
        if hasattr(response, 'statusMessage'):
            status_message = response.statusMessage
        elif hasattr(response, 'StatusMessage'):
            status_message = response.StatusMessage

        if not cdr_content:
            return {
                "error": "No se encontró CDR en la respuesta",
                "response_attributes": [attr for attr in dir(response) if not attr.startswith('_')],
                "full_response": str(response)
            }, 500

        # Guardar CDR
        cdr_filename = f'{file_name.replace(".zip", "")}-CDR.zip'
        
        # Decodificar CDR si es base64
        if isinstance(cdr_content, str):
            try:
                cdr_content = base64.b64decode(cdr_content)
            except Exception:
                cdr_content = cdr_content.encode('utf-8')
        
        with open(cdr_filename, 'wb') as f:
            f.write(cdr_content)

        logger.info(f"CDR guardado como: {cdr_filename}")

        response_info = {
            "message": "Envío exitoso a SUNAT",
            "cdr_file": cdr_filename,
            "original_file": file_name,
            "status": "success"
        }

        if status_code:
            response_info["status_code"] = status_code
        if status_message:
            response_info["status_message"] = status_message

        return response_info, 200

    except Exception as e:
        logger.error(f"Error procesando respuesta: {e}")
        return {"error": f"Error procesando respuesta SUNAT: {str(e)}"}, 500


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


def build_soap_envelope(data, user, pwd):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope 
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:br="http://service.sunat.gob.pe" 
    xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
  <soapenv:Header>
    <wsse:Security soapenv:mustUnderstand="1">
      <wsse:UsernameToken>
        <wsse:Username>{user}</wsse:Username>
        <wsse:Password>{pwd}</wsse:Password>
      </wsse:UsernameToken>
    </wsse:Security>
  </soapenv:Header>
  <soapenv:Body>
    <br:sendBill>
      <fileName>{data['fileName']}</fileName>
      <contentFile>{data['contentFile']}</contentFile>
    </br:sendBill>
  </soapenv:Body>
</soapenv:Envelope>"""


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


def send_to_sunat(xml_firmado, data, env = "qas"):
    try:
        if env == "qas":
            URL = os.getenv("sunat_qas")
        elif env == "prod":
            URL = os.getenv("sunat_prod")

        #generacion de name del file
        ruc = os.getenv("SUNAT_RUC")
        serie = data.get("documento").split("-")[0]
        correlativo = data.get("documento").split("-")[1]
        tipo_doc = "01"
        name_file = f"{ruc}-{tipo_doc}-{serie}-{correlativo}"
        nombre_xml = f"{name_file}.xml"
        nombre_zip =  f"{name_file}.zip"
        RB = "assets" # ruta_base
        print(data.get("ruc_cliente"))
        # consultar el ruc del cliente
       
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
            print("cliente",cliente)
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
        print("data",data)
        xml_string = generar_xml()  # Aquí se obtiene el XML con placeholders
        xml_string = agregar_datos_ruc_cliente(xml_string,data.get("ruc_cliente"))  # Agregar datos del RUC emisor
        xml_string = agregar_datos_ruc(xml_string,os.getenv("SUNAT_RUC"))  # Agregar datos del RUC cliente
        xml_string = xml_string.replace("@fecha", datetime.now().strftime("%Y-%m-%d"))
        xml_string = xml_string.replace("@serie", data.get("documento"))
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
        print(xml_string)
        return xml_string
        
    except Exception as e:
        print(f"❌ Error al completar el XML: {e}")
        return {"error": str(e)}, 500