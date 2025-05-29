import os  
import zipfile
def generar_xml():
    try:
        xml = """
        <Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
            xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
            xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
            xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
            xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">

    <ext:UBLExtensions>
        <ext:UBLExtension>
        <ext:ExtensionContent>
        </ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>

    <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
    <cbc:CustomizationID>2.0</cbc:CustomizationID>
    <cbc:ID>@serie</cbc:ID>
    <cbc:IssueDate>@fecha</cbc:IssueDate>
    <cbc:InvoiceTypeCode listID="0101">@tipo</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>PEN</cbc:DocumentCurrencyCode>

    <!-- Datos del emisor -->
    <cac:AccountingSupplierParty>
        <cac:Party>
        <cac:PartyLegalEntity>
            <cbc:RegistrationName>@razon_social</cbc:RegistrationName>
            <cbc:CompanyID schemeID="6">@ruc</cbc:CompanyID>
        </cac:PartyLegalEntity>
        </cac:Party>
    </cac:AccountingSupplierParty>

    <!-- Datos del cliente -->
    <cac:AccountingCustomerParty>
        <cac:Party>
        <cac:PartyLegalEntity>
            <cbc:RegistrationName>@razon_social_cliente</cbc:RegistrationName>
            <cbc:CompanyID schemeID="6">@ruc_cliente</cbc:CompanyID>
        </cac:PartyLegalEntity>
        </cac:Party>
    </cac:AccountingCustomerParty>

    <!-- Línea de detalle -->
    <cac:InvoiceLine>
        <cbc:ID>1</cbc:ID>
        <cbc:InvoicedQuantity unitCode="NIU">1</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount currencyID="@tipo_moneda">@monto</cbc:LineExtensionAmount>
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
                    <cbc:Percent>@porcentaje_igv</cbc:Percent>
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

    <!-- Totales -->
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv</cbc:TaxAmount>
        <cac:TaxSubtotal>
        <cbc:TaxableAmount currencyID="@tipo_moneda">@subtotal</cbc:TaxableAmount>
        <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv</cbc:TaxAmount>
        <cac:TaxCategory>
            <cbc:ID schemeID="UN/ECE 5305">S</cbc:ID>
            <cbc:Percent>@porcentaje_igv</cbc:Percent>
            <cbc:TaxExemptionReasonCode>10</cbc:TaxExemptionReasonCode>
            <cac:TaxScheme>
            <cbc:ID>1000</cbc:ID>
            <cbc:Name>IGV</cbc:Name>
            <cbc:TaxTypeCode>VAT</cbc:TaxTypeCode>
            </cac:TaxScheme>
        </cac:TaxCategory>
        </cac:TaxSubtotal>
    </cac:TaxTotal>

    <cac:LegalMonetaryTotal>
        <cbc:PayableAmount currencyID="@tipo_moneda">@monto_total</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
    </Invoice>  
"""
        return xml

    except Exception as e:
        print(e)


def crear_xml_y_zip(xml_firmado,data):
    try:
        # Datos básicos
        ruc = os.getenv("SUNAT_RUC")
        serie = data.get("documento").split("-")[0]
        correlativo = data.get("documento").split("-")[1]
        tipo_doc = "01"  # Factura electrónica

        nombre_xml = f"{ruc}-{tipo_doc}-{serie}-{correlativo}.xml"
        nombre_zip = nombre_xml.replace(".xml", ".zip")
        ruta_base = "assets"
        ruta_xml = os.path.join(ruta_base, nombre_xml)
        ruta_zip = os.path.join(ruta_base, nombre_zip)

        # Asegura el directorio
        os.makedirs(ruta_base, exist_ok=True)

        # Eliminar XML si existe
        if os.path.exists(ruta_xml):
            os.remove(ruta_xml)

        # Guardar el XML
        with open(ruta_xml, "w", encoding="utf-8") as f:
            f.write(xml_firmado)

        # Eliminar ZIP si existe
        if os.path.exists(ruta_zip):
            os.remove(ruta_zip)

        # Crear el ZIP
        with zipfile.ZipFile(ruta_zip, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(ruta_xml, arcname=nombre_xml)  # SUNAT exige el nombre exacto dentro del ZIP

        return {
            "xml": ruta_xml,
            "zip": ruta_zip,
            "nombre_xml": nombre_xml,
            "nombre_zip": nombre_zip
        }, 200

    except Exception as e:
        print(f"❌ Error al crear XML/ZIP: {e}")
        return None, 500