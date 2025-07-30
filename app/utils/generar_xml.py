import os
import zipfile
import io
import xml.etree.ElementTree as ET
from app.utils.utils import get_sunat_response_code, get_sunat_response_xml

import base64
# fACTURA
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
        <ext:ExtensionContent></ext:ExtensionContent>
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
        @DatosEmisor
    </cac:AccountingSupplierParty>

    <!-- Datos del cliente -->
    <cac:AccountingCustomerParty>
        @DatosCliente
    </cac:AccountingCustomerParty>

    <!-- Forma de pago -->
    <cac:PaymentTerms>
        <cbc:ID>FormaPago</cbc:ID>
        <cbc:PaymentMeansID>Contado</cbc:PaymentMeansID>
    </cac:PaymentTerms>
    <!-- Totales -->
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="@tipo_moneda">@subtotal</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv</cbc:TaxAmount>
            <cac:TaxCategory>
                <cac:TaxScheme>
                    <cbc:ID>1000</cbc:ID>
                    <cbc:Name>IGV</cbc:Name>
                    <cbc:TaxTypeCode>VAT</cbc:TaxTypeCode>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>
    </cac:TaxTotal>

    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="@tipo_moneda">@subtotal</cbc:LineExtensionAmount>
        <cbc:TaxInclusiveAmount currencyID="@tipo_moneda">@monto_total</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="@tipo_moneda">@monto_total</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
    
    <!-- Línea de detalle -->
    @detalle_productos
    </Invoice>  
"""
        return xml

    except Exception as e:
        print(e)

def generate_nc_xml():
    try:
        return """
            <CreditNote xmlns="urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">
                <ext:UBLExtensions>
                <ext:UBLExtension>
                <ext:ExtensionContent></ext:ExtensionContent>
                </ext:UBLExtension>
                </ext:UBLExtensions>
                <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
                <cbc:CustomizationID>2.0</cbc:CustomizationID>
                <cbc:ID>@serie</cbc:ID>
                <cbc:IssueDate>@fecha</cbc:IssueDate>
                <cbc:IssueTime>@hora</cbc:IssueTime>
                <cbc:Note languageLocaleID="1000"><![CDATA[@observacion]]></cbc:Note>
                <cbc:DocumentCurrencyCode>@tipo_moneda</cbc:DocumentCurrencyCode>
                <cac:DiscrepancyResponse>
                    <cbc:ResponseCode>@codigo_table</cbc:ResponseCode>
                    <cbc:Description>@codigo_mensaje_table</cbc:Description>
                </cac:DiscrepancyResponse>
                <cac:BillingReference>
                <cac:InvoiceDocumentReference>
                <cbc:ID>@document_refenced</cbc:ID>
                <cbc:DocumentTypeCode>@document_type_refenced</cbc:DocumentTypeCode>
                </cac:InvoiceDocumentReference>
                </cac:BillingReference>
                <cac:Signature>
                <cbc:ID>-</cbc:ID>
                <cac:SignatoryParty>
                    @DataRazonEmisor
                </cac:SignatoryParty>
                <cac:DigitalSignatureAttachment>
                <cac:ExternalReference>
                <cbc:URI></cbc:URI>
                </cac:ExternalReference>
                </cac:DigitalSignatureAttachment>
                </cac:Signature>
                <cac:AccountingSupplierParty>
                    @DatosEmisor
                </cac:AccountingSupplierParty>
                <cac:AccountingCustomerParty>
                    @DatosCliente
                </cac:AccountingCustomerParty>
                <cac:TaxTotal>
                    <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv</cbc:TaxAmount>
                    <cac:TaxSubtotal>
                        <cbc:TaxableAmount currencyID="@tipo_moneda">@subtotal</cbc:TaxableAmount>
                        <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv</cbc:TaxAmount>
                        <cac:TaxCategory>
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
                @detalle_productos_nc_nd
            </CreditNote>
        """
        
        
    except Exception as e:
        print(f"❌ Error generating NC XML: {e}")
        return None



def generate_nd_xml():
    try:
        xml_fragment= """
        <DebitNote xmlns="urn:oasis:names:specification:ubl:schema:xsd:DebitNote-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">
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
            <cbc:IssueTime>@hora</cbc:IssueTime>
            <cbc:Note languageLocaleID="1000"><![CDATA[@observacion]]></cbc:Note>
            <cbc:DocumentCurrencyCode>@tipo_moneda</cbc:DocumentCurrencyCode>
            <cac:DiscrepancyResponse>
                <cbc:ResponseCode>@codigo_table</cbc:ResponseCode>
                <cbc:Description>@codigo_mensaje_table</cbc:Description>
            </cac:DiscrepancyResponse>
            <cac:BillingReference>
            <cac:InvoiceDocumentReference>
            <cbc:ID>@document_refenced</cbc:ID>
            <cbc:DocumentTypeCode>@document_type_refenced</cbc:DocumentTypeCode>
            </cac:InvoiceDocumentReference>
            </cac:BillingReference>
            <cac:Signature>
            <cbc:ID>-</cbc:ID>
            <cac:SignatoryParty>
                @DataRazonEmisor
            </cac:SignatoryParty>
            <cac:DigitalSignatureAttachment>
            <cac:ExternalReference>
            <cbc:URI></cbc:URI>
            </cac:ExternalReference>
            </cac:DigitalSignatureAttachment>
            </cac:Signature>
            <cac:AccountingSupplierParty>
            @DatosEmisor
            </cac:AccountingSupplierParty>
            <cac:AccountingCustomerParty>
            @DatosCliente
            </cac:AccountingCustomerParty>
            <cac:TaxTotal>
                <cbc:TaxAmount currencyID="PEN">@monto_igv</cbc:TaxAmount>
                <cac:TaxSubtotal>
                    <cbc:TaxableAmount currencyID="@tipo_moneda">@subtotal</cbc:TaxableAmount>
                    <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv</cbc:TaxAmount>
                    <cac:TaxCategory>
                    <cac:TaxScheme>
                    <cbc:ID>1000</cbc:ID>
                    <cbc:Name>IGV</cbc:Name>
                    <cbc:TaxTypeCode>VAT</cbc:TaxTypeCode>
                    </cac:TaxScheme>
                    </cac:TaxCategory>
                </cac:TaxSubtotal>
            </cac:TaxTotal>
                <cac:RequestedMonetaryTotal>
                <cbc:PayableAmount currencyID="@tipo_moneda">@monto_total</cbc:PayableAmount>
                </cac:RequestedMonetaryTotal>
            @detalle_productos_nc_nd
        </DebitNote>
        """
        return xml_fragment
    except Exception as e:
        print(f"❌ Error generating ND XML: {e}")
        return None
    
def create_xml(xml_firmado,rb, nm_xml, flag_cdr=False):
    try:
        path_full = os.path.join(rb, nm_xml)
        
        print(f"Creating XML file at: {path_full}")
        if flag_cdr:
            print("Creating XML file for CDR")
            print("path_full", path_full)
        if(os.path.exists(path_full)):
            os.remove(path_full)
        
        
        with open(path_full, "w", encoding="utf-8") as f:
            f.write(xml_firmado)
    except Exception as e:
        print(f"❌ Error creating XML 2 file: {e}")
        return {"error": str(e)}, 500


## rb: ruta base
def create_zip(xml_firmado, rb, nm_zip, flag_cdr=False):
    try:
        path_full_zip = os.path.join(rb, nm_zip)
        name_xml_change = nm_zip.replace(".zip", ".xml") # para tener nombre en XML
        print(f"Creating ZIP file at: {name_xml_change}")
        path_full_xml = os.path.join(rb, name_xml_change)
        
          # Verify XML content before zipping
        try:
            with open(path_full_xml, 'r', encoding='utf-8') as xml_file:
                xml_content = xml_file.read()
                # Basic XML validation
                ET.fromstring(xml_content)
        except ET.ParseError as xml_err:
            return {"error": f"Invalid XML structure: {str(xml_err)}"}, 400

        
        if(os.path.exists(path_full_zip)):
            os.remove(path_full_zip)
            
        with zipfile.ZipFile(path_full_zip, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(path_full_xml, arcname=name_xml_change)
              
        if os.path.exists(path_full_zip):
            # Read and encode ZIP file
            with open(path_full_zip, "rb") as zip_file:
                zip_content = zip_file.read()
                zip_base64 = base64.b64encode(zip_content).decode('utf-8')
                
            return {
                "message": "ZIP created successfully",
                "path": path_full_zip,
                "size": os.path.getsize(path_full_zip),
                "content_base64": zip_base64
            }, 200
        else:
            print("❌ ZIP file was not created")
            raise Exception({"error": "ZIP file was not created"}, 500)
            
            
    except Exception as e:
        return {"error": str(e)}, 500


def crear_xml_y_zip(xml_firmado, data):
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
            zipf.write(
                ruta_xml, arcname=nombre_xml
            )  # SUNAT exige el nombre exacto dentro del ZIP

        return {
            "xml": ruta_xml,
            "zip": ruta_zip,
            "nombre_xml": nombre_xml,
            "nombre_zip": nombre_zip,
        }, 200

    except Exception as e:
        print(f"❌ Error al crear XML/ZIP: {e}")
        return None, 500
