  
from dotenv import load_dotenv
from .generar_xml import generar_xml, generate_nc_xml
from app.services.serie_services import get_last_number
import os
from datetime import datetime

def build_party_xml(is_business,tipo, ruc, razon_social, direccion, provincia, distrito):
    direccion_xml = ""
    if is_business:  # RUC
        direccion_xml = f"""
            <cbc:CityName>{provincia}</cbc:CityName>
            <cbc:District>{distrito}</cbc:District>
        """

    return f"""
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID="{tipo}">{ruc}</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>{razon_social}</cbc:RegistrationName>
                <cac:RegistrationAddress>
                    <cbc:AddressTypeCode>0000</cbc:AddressTypeCode>
                    {direccion_xml}
                    <cac:AddressLine>
                        <cbc:Line><![CDATA[{direccion}]]></cbc:Line>
                    </cac:AddressLine>
            </cac:RegistrationAddress>
            </cac:PartyLegalEntity>
        </cac:Party>
    """
    
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
        try:
            from app.services.customer_service import get_all_customers_by_ruc
            payload_customers=get_all_customers_by_ruc(rucs)  # Validar que los RUCs existan en la base de datos
        except Exception as e:
            print(f"❌ Error al obtener los clientes: {e}")
        
        if not payload_customers and len(payload_customers[0]) == 0:
            raise ValueError("No se encontraron clientes con los RUCs proporcionados.")
        
        
       
        
        for customer in payload_customers[0]:
            tipo =customer.get("document_type") # tipo de documento
            is_business = customer.get("is_business")
            ruc = customer.get("document_number", "")
            razon_social = customer.get("business_name", "")
            direccion = customer.get("address", "")
            provincia = customer.get("province", "")
            distrito = customer.get("city", "")
            
            party_xml = build_party_xml(is_business, tipo,ruc, razon_social, direccion, provincia, distrito)
    
        
            if customer.get("is_owner") is True:
                xml_string = xml_string.replace("@DatosEmisor", party_xml)
            else:
                xml_string = xml_string.replace("@DatosCliente", party_xml)    
        return xml_string
    except Exception as e:
        print(f"❌ Error al completar los datos del cliente: {e}")
        return {"error": str(e)}, 500


def complete_details_products(xml_string, productos):
    """
    Agrega los detalles de los productos al XML.
    """
    #  tambien hay una tabla de los unitCode que se pueden usar
    name_catalog = "CAT_07_IGV"
    try:
        from app.services.master_data_service import get_master_data_by_catalog
        
        xml_productos =[]
        catalog_07= get_master_data_by_catalog(name_catalog,productos.get("afecto_tributo"))
        if catalog_07[1] != 200:
            raise ValueError(f"No se encontró el catálogo {name_catalog} para el código de afectación tributaria {productos.get('afecto_tributo')}")
        xml_afecto_tributo = f"""
                <cbc:TaxExemptionReasonCode>{catalog_07[0].get("code")}</cbc:TaxExemptionReasonCode>
                        <cac:TaxScheme>
                            <cbc:ID>{catalog_07[0].get("value")}</cbc:ID>
                            <cbc:Name>IGV</cbc:Name>
                            <cbc:TaxTypeCode>VAT</cbc:TaxTypeCode>
                        </cac:TaxScheme>
            """
            
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
                        @xml_afecto_tributo
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
                .replace("@xml_afecto_tributo", xml_afecto_tributo)
            )
            xml_productos.append(xml_producto)
        xml_string = xml_string.replace("@detalle_productos", "".join(xml_productos))
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
        # validate of xml is required
        if data.get("type_document") in ["01","03"]:
            xml_string = generar_xml()  # Aquí se obtiene el XML con placeholders
        else:
            xml_string = generate_nc_xml()
            
        rucs = [os.getenv("SUNAT_RUC"), data.get("ruc_cliente")]
        xml_string = complete_data_customers(xml_string, rucs)  # Completar datos del cliente
        xml_string = xml_string.replace("@fecha", datetime.now().strftime("%Y-%m-%d"))
        try:
           serie_number = get_last_number(data.get("type_document"), data.get("document").split("-")[0])
        #    serie_number = data.get("documento")
        except Exception as e:
            raise ValueError(f"Error al obtener el tipo de documento. Asegúrate de que el campo 'documento' esté presente en los datos. {e}")
        xml_string = xml_string.replace("@serie", serie_number.get("serie", ""))
        xml_string = xml_string.replace("@tipo_moneda", "PEN")
        xml_string = xml_string.replace("@tipo",data.get("type_document"))  # Default to '01' if not provided
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
    