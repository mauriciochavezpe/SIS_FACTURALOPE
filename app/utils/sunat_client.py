import os
from datetime import datetime
from zeep.wsse.username import UsernameToken
from zeep import Client, Transport
import zipfile
import io
from xml.etree import ElementTree as ET

from .xml_generate import (complete_details_products,complete_data_xml)
from app.config.certificado import firmar_xml_con_placeholder
from .utils import get_sunat_response_code, get_sunat_response_xml
# obs 
from .generar_xml import create_xml, create_zip,generar_xml

def send_to_sunat(data, env = "qas"):
    try:
        if env == "qas":
            URL = os.getenv("sunat_qas")
        elif env == "prod":
            URL = os.getenv("sunat_prod")

        # Generar el XML con los datos completos
        xml_string, serie_number = complete_data_xml(data) # luego de completar los datos, se firma el XML

        #generacion de name del file
        ruc = os.getenv("SUNAT_RUC")
        tipo_doc = "01"
        name_file = f"{ruc}-{tipo_doc}-{serie_number.get('serie')}" # Ej: 20512345678-01-F001-00000001
        nombre_xml = f"{name_file}.xml"
        nombre_zip =  f"{name_file}.zip"
        RB = "assets" # ruta_base,
        tax = str(int(data.get("monto_igv")) / 100)
        try:
            create_structure_invoice = {
                                        "date": datetime.now(),
                                        "customer_id": data.get("customer_id", 1),  # Si no hay customer_id, usar 1 como dummy
                                        "num_invoice": f"{serie_number.get('correlativo'):08d}",
                                        "serie": serie_number.get("serie").split("-")[0],
                                        "subtotal": data.get("subtotal"),
                                        "total": data.get("monto_total"),
                                        "details": [
                                            {
                                                "product_id": item.get("producto_id", 1),  # Si no hay producto_id, usar 1 como dummy
                                                "quantity": item.get("quantity"),
                                                "unit_price": item.get("monto_total"),
                                                "discount": item.get("descuento", 0),
                                                "subtotal": item.get("subtotal"),
                                                "tax": tax,
                                                "total": item.get("monto_total")
                                            } for item in data.get("details", [])]
                                        }
            # print("create_structure_invoice",create_structure_invoice)
        except Exception as e:
            return {"error": f"Error al interpretar los datos del invoice {e}"}, 500
        
        # agregamos los items de la factura y procedemos a firmar el XML
        xml_string = complete_details_products(xml_string, data)
        xml_firmado = firmar_xml_con_placeholder(xml_string) # Firmar el XML
        try:
            #guardamos el file en la carpeta assets
            create_xml(xml_firmado,RB, nombre_xml,flag_cdr=False) # flag_cdr=False porque no es un CDR
            payload_zip, status= create_zip(xml_firmado,RB, nombre_zip,flag_cdr=False) # flag_cdr=False porque no es un CDR
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
            result = descomprimir_cdr(payload) #CDR es un documento que envia sunat
            ## agregar factura a la base de datos
            # agregamos los datos de la factura a la base de datos
            try:
                from app.services.invoice_service import crear_factura_standard
                print("📥 Guardando factura en la base de datos...")
                crear_factura_standard(create_structure_invoice)
            except Exception as e:
                print("❌ Error al crear la factura en la base de datos:", str(e))
                raise(e)
            
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
            xml_str = xml_bytes.decode("utf-8")
            # la ruta
            carpeta_cdr = "CDR"
            create_xml(xml_str, carpeta_cdr, nombre_xml,flag_cdr=True)
            # create_zip(xml_bytes, carpeta_cdr, nombre_xml,flag_cdr=True)

            return read_xml_cdr(xml_bytes,nombre_xml)

    except zipfile.BadZipFile as e:
        print("❌ Error al descomprimir el CDR:", str(e))
        raise
    except Exception as e:
        print("❌ Error al descomprimir el CDR:", str(e))
        raise
    

def read_xml_cdr(xml_bytes, name):
    try:

        #Crear el XML
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

