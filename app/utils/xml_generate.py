  
from dotenv import load_dotenv
from .generar_xml import create_xml, create_zip,generar_xml
from app.services.customer_service import get_all_customers_by_ruc
from app.services.serie_services import get_last_number
import os
from datetime import datetime

  
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
        tax = str(int(float(productos.get("monto_igv", "0"))) / 100)
        items = productos.get("details", [])
        ## como rrecorrer el loop de productos
        ln = len(items) # longitud de los detalles de productos
        for i in range(ln):
            producto = items[i]
            xml_producto = (
                fragmento_xml
                .replace("@index", str(i + 1))  # Usar i+1 para que empiece desde 1
                .replace("@id_producto", str(producto.get("product_id", "")))
                .replace("@cantidad", str(producto.get("quantity", "")))
                .replace("@tipo_moneda", "PEN")
                .replace("@subtotal", str(producto.get("subtotal", "")))
                .replace("@monto_total", str(producto.get("monto_total", "")))
                .replace("@tax_igv", productos.get("monto_igv", "0"))
                .replace("@monto_igv", tax)
                .replace("@descripcion", producto.get("description", ""))
            )
            xml_productos.append(xml_producto)
        xml_string = xml_string.replace("@detalle_productos", "".join(xml_productos))
        print("XML de productos agregado correctamente")
        return xml_string
    except Exception as e:
        print(f"❌ Error al agregar los detalles de los productos: {e}")
        return {"error": str(e)}, 500
    

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
        monto_igv = 0
        xml_string = generar_xml()  # Aquí se obtiene el XML con placeholders
        rucs = [os.getenv("SUNAT_RUC"), data.get("ruc_cliente")]
        xml_string = complete_data_customers(xml_string, rucs)  # Completar datos del cliente
        xml_string = xml_string.replace("@fecha", datetime.now().strftime("%Y-%m-%d"))
        try:
           serie_number = get_last_number(data.get("tipo_documento"), data.get("documento").split("-")[0])
        except Exception as e:
            raise ValueError(f"Error al obtener el tipo de documento. Asegúrate de que el campo 'documento' esté presente en los datos. {e}")
        xml_string = xml_string.replace("@serie", serie_number.get("serie"))
        xml_string = xml_string.replace("@tipo_moneda", "PEN")
        xml_string = xml_string.replace("@tipo", "01")
        xml_string = xml_string.replace("@monto_total", data.get("monto_total"))
        
        if data.get("monto_igv") is None:
            monto_igv = "0"
        else:
            monto_igv = str(int(data.get("monto_igv")) / 100)
        xml_string = xml_string.replace("@monto_igv",monto_igv)
        xml_string = xml_string.replace("@subtotal", data.get("subtotal"))
        return xml_string, serie_number
        
    except Exception as e:
        print(f"❌ Error al completar el XML: {e}")
        return {"error": str(e)}, 500
    