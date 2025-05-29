import os
import base64
from zeep import Client, Transport
from zeep.wsse.username import UsernameToken    
from requests import Session
from requests.auth import HTTPBasicAuth
import logging
from zeep.settings import Settings
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

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