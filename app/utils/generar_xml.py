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
        <cac:Party>
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
        </cac:Party>
    </cac:AccountingSupplierParty>

    <!-- Datos del cliente -->
    <cac:AccountingCustomerParty>
        <cac:Party>
        <cac:PartyIdentification>
            <cbc:ID schemeID="6">@ruc1</cbc:ID>
        </cac:PartyIdentification>
        <cac:PartyLegalEntity>
            <cbc:RegistrationName>@razon_social1</cbc:RegistrationName>
             <cac:RegistrationAddress>
                <cbc:AddressTypeCode>0000</cbc:AddressTypeCode>
                <cbc:CityName>@provincia1</cbc:CityName>
                <cbc:District>@distrito1</cbc:District>
                <cac:AddressLine>
                    <cbc:Line><![CDATA[@direccion1]]></cbc:Line>
                </cac:AddressLine>
            </cac:RegistrationAddress>
        </cac:PartyLegalEntity>
        </cac:Party>
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


def xml_boleta():
    try:
        xml = """
            <Invoice xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ccts="urn:un:unece:uncefact:documentation:2" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:qdt="urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2" xmlns:udt="urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2" xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2">
           
            <ext:UBLExtensions>
            <ext:UBLExtension>
            <ext:ExtensionContent>
            <ds:Signature Id="NubeFacTSign">
            </ds:Signature>
            </ext:ExtensionContent>
            </ext:UBLExtension>
            </ext:UBLExtensions>


            <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
            <cbc:CustomizationID>2.0</cbc:CustomizationID>
            <cbc:ID>@serie</cbc:ID>
            <cbc:IssueDate>@fecha</cbc:IssueDate>
            <cbc:IssueTime>@hora</cbc:IssueTime>
            <cbc:InvoiceTypeCode listID="0101" listAgencyName="PE:SUNAT" listName="Tipo de Documento" listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo01" name="Tipo de Operacion" listSchemeURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo51">03</cbc:InvoiceTypeCode>
            <cbc:Note languageLocaleID="1000"><![CDATA[@monto_total_letras]]></cbc:Note>
            <cbc:DocumentCurrencyCode listID="ISO 4217 Alpha" listAgencyName="United Nations Economic Commission for Europe" listName="Currency">@tipo_moneda</cbc:DocumentCurrencyCode>
            <cac:Signature>
                <cbc:ID>-</cbc:ID>
                <cac:SignatoryParty>
                <cac:PartyIdentification>
                    <cbc:ID schemaID="6">@ruc</cbc:ID>
                </cac:PartyIdentification>
                <cac:PartyName>
                <cbc:Name><![CDATA[@razon_social]]></cbc:Name>
                </cac:PartyName>
                </cac:SignatoryParty>
                <cac:DigitalSignatureAttachment>
                <cac:ExternalReference>
                <cbc:URI>@ruc</cbc:URI>
                </cac:ExternalReference>
                </cac:DigitalSignatureAttachment>
            </cac:Signature>
            <cac:AccountingSupplierParty>
            <cac:Party>
            <cac:PartyIdentification>
            <cbc:ID schemeID="6" schemeName="Documento de Identidad" schemeAgencyName="PE:SUNAT" schemeURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo06">@ruc</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
            <cbc:Name><![CDATA[@razon_social]]></cbc:Name>
            </cac:PartyName>
            <cac:PartyLegalEntity>
            <cbc:RegistrationName><![CDATA[@razon_social]]></cbc:RegistrationName>
            <cac:RegistrationAddress>
            <cbc:ID schemeName="Ubigeos" schemeAgencyName="PE:INEI">@ubigeo</cbc:ID>
            <cbc:AddressTypeCode listAgencyName="PE:SUNAT" listName="Establecimientos anexos">0000</cbc:AddressTypeCode>
            </cac:RegistrationAddress>
            </cac:PartyLegalEntity>
            </cac:Party>
            </cac:AccountingSupplierParty>
            <cac:AccountingCustomerParty>
            <cac:Party>
            <cac:PartyIdentification>
            <cbc:ID schemeID="1" schemeName="Documento de Identidad" schemeAgencyName="PE:SUNAT" schemeURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo06">@DNI_cliente</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyLegalEntity>
            <cbc:RegistrationName><![CDATA[@nombre_cliente]]></cbc:RegistrationName>
            <cac:RegistrationAddress>
            <cac:AddressLine>
            <cbc:Line><![CDATA[@direccion_cliente]]></cbc:Line>
            </cac:AddressLine>
            </cac:RegistrationAddress>
            </cac:PartyLegalEntity>
            </cac:Party>
            </cac:AccountingCustomerParty>
            <cac:TaxTotal>
            <cbc:TaxAmount currencyID="PEN">0.00</cbc:TaxAmount>
            <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="PEN">21789.00</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="PEN">0.00</cbc:TaxAmount>
            <cac:TaxCategory>
            <cac:TaxScheme>
            <cbc:ID schemeName="Codigo de tributos" schemeAgencyName="PE:SUNAT" schemeURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo05">9998</cbc:ID>
            <cbc:Name>INA</cbc:Name>
            <cbc:TaxTypeCode>FRE</cbc:TaxTypeCode>
            </cac:TaxScheme>
            </cac:TaxCategory>
            </cac:TaxSubtotal>
            </cac:TaxTotal>
            <cac:LegalMonetaryTotal>
            <cbc:LineExtensionAmount currencyID="PEN">21789.00</cbc:LineExtensionAmount>
            <cbc:TaxInclusiveAmount currencyID="PEN">21789.00</cbc:TaxInclusiveAmount>
            <cbc:AllowanceTotalAmount currencyID="PEN">0.00</cbc:AllowanceTotalAmount>
            <cbc:ChargeTotalAmount currencyID="PEN">0.00</cbc:ChargeTotalAmount>
            <cbc:PrepaidAmount currencyID="PEN">0.00</cbc:PrepaidAmount>
            <cbc:PayableAmount currencyID="PEN">21789.00</cbc:PayableAmount>
            </cac:LegalMonetaryTotal>
            <cac:InvoiceLine>
                <cbc:ID>1</cbc:ID>
                <cbc:InvoicedQuantity unitCode="ZZ" unitCodeListID="UN/ECE rec 20" unitCodeListAgencyName="United Nations Economic Commission for Europe">6000.0</cbc:InvoicedQuantity>
                <cbc:LineExtensionAmount currencyID="PEN">21789.00</cbc:LineExtensionAmount>
                <cac:PricingReference>
                <cac:AlternativeConditionPrice>
                <cbc:PriceAmount currencyID="PEN">3.6315</cbc:PriceAmount>
                <cbc:PriceTypeCode listAgencyName="PE:SUNAT" listName="Tipo de Precio" listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo16">01</cbc:PriceTypeCode>
                </cac:AlternativeConditionPrice>
                </cac:PricingReference>
                <cac:TaxTotal>
                    <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv</cbc:TaxAmount>
                    <cac:TaxSubtotal>
                        <cbc:TaxableAmount currencyID="@tipo_moneda">@monto_subtotal</cbc:TaxableAmount>
                        <cbc:TaxAmount currencyID="@tipo_moneda">@monto_igv</cbc:TaxAmount>
                        <cac:TaxCategory>
                            <cbc:Percent>@valor_igv</cbc:Percent>
                            <cbc:TaxExemptionReasonCode listAgencyName="PE:SUNAT" listName="Afectacion del IGV" listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo07">10</cbc:TaxExemptionReasonCode>
                            <cac:TaxScheme>
                                <cbc:ID schemeName="Codigo de tributos" schemeAgencyName="PE:SUNAT" schemeURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo05">1000</cbc:ID>
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
                    <cbc:PriceAmount currencyID="@tipo_moneda">@valor_unitario</cbc:PriceAmount>
                </cac:Price>
            </cac:InvoiceLine>
            </Invoice>
        """
        return xml
    except Exception as e:
        print(e)


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
