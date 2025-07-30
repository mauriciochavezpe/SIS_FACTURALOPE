  
from dotenv import load_dotenv
from .generar_xml import generar_xml, generate_nc_xml,generate_nd_xml
from app.services.serie_services import get_last_number
import os
from datetime import datetime
from app.utils.utils import build_note_amount_text

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
def build_data_razon_emisor(tipo,ruc, razon_social):
    return f"""
        <cac:PartyIdentification>
            <cbc:ID schemeID="{tipo}">{ruc}</cbc:ID>
        </cac:PartyIdentification>
        <cac:PartyName>
            <cbc:Name><![CDATA[{razon_social}]]></cbc:Name>
        </cac:PartyName>
    """
def complete_data_customers(xml_string, rucs, type=""):
    
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
            payload_customers,status=get_all_customers_by_ruc(rucs)  # Validar que los RUCs existan en la base de datos
            print(f"payload_customers: {len(payload_customers)}")
        except Exception as e:
            print(f"❌ Error al obtener los clientes: {e}")
        
        if len(payload_customers) == 0:
            raise ValueError("No se encontraron clientes con los RUCs proporcionados.")
        
        
       
        
        for index,customer in enumerate(payload_customers):
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
                if(type in ["07","08"]):
                    fragment_owner = build_data_razon_emisor(tipo,ruc, razon_social)
                    xml_string = xml_string.replace("@DataRazonEmisor", fragment_owner)
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
        igv = productos.get("monto_igv", "0")
        tax = str(int(float(igv)) / 100) #
        print(f"igv: {igv}, tax: {tax}")
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
                .replace("@tax_igv", igv)
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
    
def complete_details_NC_ND(xml_string, data): # nota de credito <CreditNoteLime>  <DebitNoteLine>
    try:
        etag = "CreditNoteLine" if data.get("document_type") == "07" else "DebitNoteLine"
        fragmento_xml = f"""
        <cac:{etag}>
                    <cbc:ID>@index</cbc:ID>
                    <cbc:CreditedQuantity unitCode="NIU">@quantity</cbc:CreditedQuantity>
                    <cbc:LineExtensionAmount currencyID="@tipo_moneda">@unit_price</cbc:LineExtensionAmount>
                        <cac:PricingReference>
                        <cac:AlternativeConditionPrice>
                        <cbc:PriceAmount currencyID="@tipo_moneda">@monto_total</cbc:PriceAmount>
                        <cbc:PriceTypeCode>01</cbc:PriceTypeCode>
                        </cac:AlternativeConditionPrice>
                        </cac:PricingReference>
                    <cac:TaxTotal>
                        <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv_dec</cbc:TaxAmount>
                        <cac:TaxSubtotal>
                            <cbc:TaxableAmount currencyID="@tipo_moneda">@unit_price</cbc:TaxableAmount>
                            <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv_dec</cbc:TaxAmount>
                            <cac:TaxCategory>
                            <cbc:Percent>@monto_igv</cbc:Percent>
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
                        <cbc:PriceAmount currencyID="@tipo_moneda">@unit_price</cbc:PriceAmount>
                    </cac:Price>
                </cac:{etag}>"""
                
        if data.get("details") and len(data.get("details")) > 0:
            items = data.get("details", [])
            xml_productos = []
            
            igv_dec = str(int(data.get("monto_igv", "0")) / 100) # 0.18
            for i, producto in enumerate(items):
                xml_producto = (
                    fragmento_xml
                    .replace("@index", str(i+1))  # Usar i+1 para que empiece desde 1
                    .replace("@monto_igv_dec", igv_dec)
                    .replace("@monto_igv", data.get("monto_igv", "0"))
                    .replace("@tipo_moneda", "PEN")
                    .replace("@quantity", producto.get("quantity", ""))
                    .replace("@unit_price", producto.get("unit_price", ""))
                    .replace("@monto_total", producto.get("monto_total", ""))
                    .replace("@descripcion", producto.get("description", ""))
                )
                xml_productos.append(xml_producto)
            xml_string = xml_string.replace("@detalle_productos_nc_nd", "".join(xml_productos))
        return xml_string
    except Exception as e:
        print(f"❌ Error al completar los detalles de la Nota de Crédito: {e}")
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
        document_type = data.get("document_type")  # Default to '01' if not provided
        # validate of xml is required
        if document_type in ["01","03"]:
            xml_string = generar_xml()  # Aquí se obtiene el XML con placeholders
        elif document_type == "07":
            xml_string = generate_nc_xml()
        else:
            xml_string = generate_nd_xml()  # Default to '01' if not provided
        rucs = [os.getenv("SUNAT_RUC"), data.get("ruc_cliente")]
        xml_string = complete_data_customers(xml_string, rucs, document_type)  # Completar datos del cliente
        xml_string = xml_string.replace("@fecha", datetime.now().strftime("%Y-%m-%d"))
        xml_string = xml_string.replace("@hora", datetime.now().strftime("%H:%M:%S"))
        serie_num = data.get("document", "").split("-")
        serie_num = f"{serie_num[0]}-{int(serie_num[1]):08d}"
        
        xml_string = xml_string.replace("@serie", serie_num)
        xml_string = xml_string.replace("@tipo_moneda", "PEN")
        xml_string = xml_string.replace("@tipo",document_type)  # Default to '01' if not provided
        xml_string = xml_string.replace("@monto_total", data.get("monto_total"))
        
        if document_type in ["07","08"]:
            
            # buscar la factura por el tipo de serie y número
            try:
                from app.services.invoice_service import get_invoice_by_serie_num
                invoice_relative,status = get_invoice_by_serie_num(data.get("relative_document"))
                
                if invoice_relative is None:
                    raise ValueError({"error": "Factura relacionada no encontrada."})
            except Exception as e:
                print(f"❌ Error al obtener la factura relacionada: {e}")
                return {"error": str(e)}, 400
            
            serie_num_relative = invoice_relative.get("serie") + "-" + str(invoice_relative.get("num_invoice")).zfill(8)
            xml_string = complete_details_NC_ND(xml_string, data)
            xml_string = xml_string.replace("@observacion", build_note_amount_text(data.get("monto_total", "0"), "SOLES"))
            xml_string = xml_string.replace("@codigo_table", data.get("codigo_table", ""))
            xml_string = xml_string.replace("@codigo_mensaje_table", data.get("codigo_mensaje_table", ""))
            xml_string = xml_string.replace("@document_refenced", serie_num_relative)
            xml_string = xml_string.replace("@document_type_refenced", str(invoice_relative.get("document_type", "")).zfill(2))
        
        
        
        if data.get("monto_igv") is None:
            monto_igv = "0"
        else:
            monto_igv = str(int(data.get("monto_igv")) / 100)
        xml_string = xml_string.replace("@monto_igv",monto_igv)
        xml_string = xml_string.replace("@subtotal", data.get("subtotal"))
        return xml_string, serie_num
        
    except Exception as e:
        print(f"❌ Error al completar el XML: {e}")
        return {"error": str(e)}, 500
    