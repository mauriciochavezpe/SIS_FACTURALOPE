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
from .generar_xml import create_xml, create_zip,generar_xml
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


def send_to_sunat(xml_string, info_xml,data, env = "qas"):
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
        RB = "assets" # ruta_base,
        carpeta_CRD = "CDR" # carpeta donde se guardan los CDRs
        try:
            create_structure_invoice = {
                                        "date": datetime.now(),
                                        "customer_id": data.get("customer_id", 1),  # Si no hay customer_id, usar 1 como dummy
                                        "num_invoice": f"{info_xml.get('correlativo'):08d}",
                                        "serie": info_xml.get("serie").split("-")[0],
                                        "subtotal": data.get("subtotal"),
                                        "total": data.get("monto_total"),
                                        "details": [
                                            {
                                                "product_id": item.get("producto_id", 1),  # Si no hay producto_id, usar 1 como dummy
                                                "quantity": item.get("cantidad"),
                                                "unit_price": item.get("monto_total"),
                                                "discount": item.get("descuento", 0),
                                                "subtotal": item.get("subtotal"),
                                                "tax": item.get("monto_igv"),
                                                "total": item.get("monto_total")
                                            } for item in data.get("details", [])]
                                        }
        except Exception as e:
            return {"error": "Error al interpretar los datos del invoice"}, 500
        
        # agregamos los items de la factura y procedemos a firmar el XML
        xml_string = complete_details_products(xml_string, data.get("details", []))
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
            result = descomprimir_cdr(payload)
            ## agregar factura a la base de datos
            # agregamos los datos de la factura a la base de datos
            try:
                print("📥 Guardando factura en la base de datos...")
                # crear_factura_standard(create_structure_invoice)
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
        rucs = [os.getenv("SUNAT_RUC"), data.get("ruc_cliente")]
        xml_string = complete_data_customers(xml_string, rucs)  # Completar datos del cliente
        # xml_string = agregar_datos_ruc_cliente(xml_string,data.get("ruc_cliente"))  # Agregar datos del RUC emisor
        # xml_string = agregar_datos_ruc(xml_string,os.getenv("SUNAT_RUC"))  # Agregar datos del RUC cliente
        xml_string = xml_string.replace("@fecha", datetime.now().strftime("%Y-%m-%d"))
        try:
           serie_number = get_last_number(data.get("tipo_documento"), data.get("documento").split("-")[0])
        except Exception as e:
            raise ValueError(f"Error al obtener el tipo de documento. Asegúrate de que el campo 'documento' esté presente en los datos. {e}")
        xml_string = xml_string.replace("@serie", serie_number.get("serie"))
        xml_string = xml_string.replace("@tipo_moneda", "PEN")
        xml_string = xml_string.replace("@tipo", "01")
        xml_string = xml_string.replace("@monto_total", data.get("monto_total"))
        # xml_string = firmar_xml_con_placeholder(xml_string) # Firmar el XML
        xml_string = xml_string.replace("@monto_igv", data.get("monto_igv"))
        xml_string = xml_string.replace("@subtotal", data.get("subtotal"))
        return xml_string, serie_number
        
    except Exception as e:
        print(f"❌ Error al completar el XML: {e}")
        return {"error": str(e)}, 500
    
def complete_data_customers(xml_string, rucs):
    """
    Completa el XML con los datos del cliente.

    Args:
        xml_string (str): XML con placeholders, expected to contain tags for customer details.
        rucs (list): List of RUCs (Registro Único de Contribuyente) as strings to validate and fetch customer data.

    Returns:
        str: XML string with customer details filled in, formatted according to the SUNAT specifications.
    """
    try:
        payload_customers=get_all_customers_by_ruc(rucs)  # Validar que los RUCs existan en la base de datos
        if len(payload_customers[0]) == 0:
            raise ValueError("No se encontraron clientes con los RUCs proporcionados.")
        xml_template ="""
            <cac:PartyIdentification>
                <cbc:ID schemeID="6">@ruc</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>@razon_social</cbc:RegistrationName>
                <cac:RegistrationAddress>
                    <cbc:AddressTypeCode>0000</cbc:AddressTypeCode>
                    <cbc:CityName>@provincia</cbc:CityName>
                    <cbc:District>@distrito</cbc:District>
                    <cac:AddressLine>
                        <cbc:Line><![CDATA[@direccion]]></cbc:Line>
                    </cac:AddressLine>
                </cac:RegistrationAddress>
            </cac:PartyLegalEntity>
        """
              
        # print("client", len(payload_customers[0]))
        for custormer in payload_customers[0]:
            xml_customers = xml_template
            xml_customers = xml_customers.replace("@ruc", custormer.get("document_number", ""))
            xml_customers = xml_customers.replace("@razon_social", custormer.get("business_name"))
            xml_customers = xml_customers.replace("@direccion", custormer.get("address", ""))
            xml_customers = xml_customers.replace("@provincia", custormer.get("province", ""))
            xml_customers = xml_customers.replace("@distrito", custormer.get("city", ""))  
            if custormer.get("is_owner") is True:
                xml_string = xml_string.replace("@DatosEmisor", xml_customers)
            else:
                xml_string = xml_string.replace("@DatosCliente", xml_customers)    
            print("xml_string", xml_customers)
        return xml_string
    except Exception as e:
        print(f"❌ Error al completar los datos del cliente: {e}")
        return {"error": str(e)}, 500
    
def complete_details_products(xml_string, productos):
    """
    Agrega los detalles de los productos al XML.
    """
    #  tambien hay una tabla de los unitCode que se pueden usar
    try:
        xml_productos =[]
        fragmento_xml = """
        <!-- Detalle de productos @index-->
        <cac:InvoiceLine>
            <cbc:ID>@id_producto</cbc:ID>
            <cbc:InvoicedQuantity unitCode="NIU">@cantidad</cbc:InvoicedQuantity>
            <cbc:LineExtensionAmount currencyID="@tipo_moneda">@subtotal</cbc:LineExtensionAmount>
            <cac:PricingReference>
                <cac:AlternativeConditionPrice>
                    <cbc:PriceAmount currencyID="@tipo_moneda">@monto_total</cbc:PriceAmount>
                    <cbc:PriceTypeCode>01</cbc:PriceTypeCode>
                </cac:AlternativeConditionPrice>
            </cac:PricingReference>
            <cac:TaxTotal>
                <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv</cbc:TaxAmount>
                <cac:TaxSubtotal>
                    <cbc:TaxableAmount currencyID="@tipo_moneda">@subtotal</cbc:TaxableAmount>
                    <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv</cbc:TaxAmount>
                    <cac:TaxCategory>
                        <cbc:Percent>@tax_igv</cbc:Percent>
                        <cbc:TaxExemptionReasonCode>10</cbc:TaxExemptionReasonCode>
                        <cac:TaxScheme>
                            <cbc:ID>1000</cbc:ID>
                            <cbc:Name>IGV</cbc:Name>
                            <cbc:TaxTypeCode>VAT</cbc:TaxTypeCode>
                        </cac:TaxScheme>
                    </cac:TaxCategory>
                </cac:TaxSubtotal>
            </cac:TaxTotal>
            <cac:Item>
                <cbc:Description>@descripcion</cbc:Description>
            </cac:Item>
            <cac:Price>
                <cbc:PriceAmount currencyID="@tipo_moneda">@monto_total</cbc:PriceAmount>
            </cac:Price>
        </cac:InvoiceLine>
        
        """
        ## como rrecorrer el loop de productos
        for i in range(len(productos)):
            producto = productos[i]
            xml_producto = (
                fragmento_xml
                .replace("@index", str(i + 1))  # Usar i+1 para que empiece desde 1
                .replace("@id_producto", str(producto.get("product_id", "")))
                .replace("@cantidad", str(producto.get("quantity", "")))
                .replace("@tipo_moneda", "PEN")
                .replace("@subtotal", str(producto.get("subtotal", "")))
                .replace("@monto_total", str(producto.get("monto_total", "")))
                .replace("@monto_igv", str(producto.get("monto_igv", "")))
                .replace("@tax_igv", str(producto.get("tax", "")))
                .replace("@descripcion", str(producto.get("description", "")))
            )
            xml_productos.append(xml_producto)
        xml_string = xml_string.replace("@detalle_productos", "".join(xml_productos))
        return xml_string
    except Exception as e:
        print(f"❌ Error al agregar los detalles de los productos: {e}")
        return {"error": str(e)}, 500
    