
"""
Este módulo se encarga de generar fragmentos de XML y ensamblar el XML final
para los documentos electrónicos de SUNAT. NO debe realizar llamadas a servicios.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

from app.utils.utils import build_note_amount_text
from app.utils.xml_utils.xml_templates import (
    CREDIT_NOTE_TEMPLATE, DEBIT_NOTE_TEMPLATE, INVOICE_TEMPLATE)

from app.utils.utils_constantes import (UNIT_CODE_NIU,
PRICE_TYPE_CODE_MAIN,PLACEHOLDER_OBSERVACION,
CURRENCY_PEN,TAX_NAME_IGV,TAX_TYPE_CODE_VAT,PLACEHOLDER_DATOS_EMISOR,PLACEHOLDER_DETALLE_PRODUCTOS,PLACEHOLDER_DETALLE_PRODUCTOS_NC_ND,
                                        PLACEHOLDER_DATA_RAZON_EMISOR,PLACEHOLDER_DATOS_CLIENTE,
                                        CATALOG_07_IGV,PLACEHOLDER_FECHA,PLACEHOLDER_HORA,
                                        PLACEHOLDER_SERIE,PLACEHOLDER_TIPO_MONEDA,PLACEHOLDER_TIPO_DOCUMENTO,
                                        PLACEHOLDER_MONTO_TOTAL,PLACEHOLDER_SUBTOTAL,PLACEHOLDER_MONTO_IGV,
                                        PLACEHOLDER_CODIGO_TABLA,PLACEHOLDER_CODIGO_MENSAJE_TABLA,PLACEHOLDER_DOCUMENTO_REFERENCIADO,
                                        PLACEHOLDER_TIPO_DOCUMENTO_REFERENCIADO)
# Cargar variables de entorno
load_dotenv()


# --- XML Building Functions ---

def _build_party_xml(is_business: bool, tipo: str, ruc: str, razon_social: str,
                     direccion: str, provincia: str, distrito: str) -> str:
    """Construye el fragmento XML para una parte (emisor o cliente)."""
    direccion_xml = ""
    if is_business:
        direccion_xml = f'''
            <cbc:CityName>{provincia}</cbc:CityName>
            <cbc:District>{distrito}</cbc:District>
        '''

    return f'''
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
    '''


def _build_data_razon_emisor_xml(tipo: str, ruc: str, razon_social: str) -> str:
    """Construye el fragmento XML con los datos de la razón social del emisor."""
    return f'''
        <cac:PartyIdentification>
            <cbc:ID schemeID="{tipo}">{ruc}</cbc:ID>
        </cac:PartyIdentification>
        <cac:PartyName>
            <cbc:Name><![CDATA[{razon_social}]]></cbc:Name>
        </cac:PartyName>
    '''


def _get_xml_template(document_type: str) -> str:
    """Selecciona la plantilla XML adecuada según el tipo de documento."""
    if document_type in ["01", "03"]:
        return INVOICE_TEMPLATE
    if document_type == "07":
        return CREDIT_NOTE_TEMPLATE
    if document_type == "08":
        return DEBIT_NOTE_TEMPLATE
    raise ValueError(f"Tipo de documento no válido: {document_type}")


# --- Data Completion Functions ---

def _complete_customer_data(xml_string: str, payload_customers: List[Dict[str, Any]], document_type: str) -> str:
    """Completa el XML con los datos del emisor y cliente a partir de los datos proporcionados."""
    if not payload_customers:
        raise ValueError("No se proporcionaron datos de clientes.")

    for customer in payload_customers:
        party_xml = _build_party_xml(
            is_business=customer.get("is_business"),
            tipo=customer.get("document_type"),
            ruc=customer.get("document_number", ""),
            razon_social=customer.get("business_name", ""),
            direccion=customer.get("address", ""),
            provincia=customer.get("province", ""),
            distrito=customer.get("city", "")
        )

        if customer.get("is_owner"):
            xml_string = xml_string.replace(PLACEHOLDER_DATOS_EMISOR, party_xml)
            if document_type in ["07", "08"]:
                fragment_owner = _build_data_razon_emisor_xml(
                    tipo=customer.get("document_type"),
                    ruc=customer.get("document_number", ""),
                    razon_social=customer.get("business_name", "")
                )
                xml_string = xml_string.replace(
                    PLACEHOLDER_DATA_RAZON_EMISOR, fragment_owner)
        else:
            xml_string = xml_string.replace(PLACEHOLDER_DATOS_CLIENTE, party_xml)
    return xml_string


def _complete_product_details(xml_string: str, productos: Dict[str, Any], catalog_07: Dict[str, Any]) -> str:
    """Agrega los detalles de los productos al XML de la factura."""
    if not catalog_07:
        raise ValueError(
            f"No se proporcionaron datos del catálogo {CATALOG_07_IGV}")

    xml_afecto_tributo = f'''
        <cbc:TaxExemptionReasonCode>{catalog_07.get("code")}</cbc:TaxExemptionReasonCode>
        <cac:TaxScheme>
            <cbc:ID>{catalog_07.get("value")}</cbc:ID>
            <cbc:Name>{TAX_NAME_IGV}</cbc:Name>
            <cbc:TaxTypeCode>{TAX_TYPE_CODE_VAT}</cbc:TaxTypeCode>
        </cac:TaxScheme>
    '''

    fragmento_xml_base = """
        <cac:InvoiceLine>
            <cbc:ID>{id_producto}</cbc:ID>
            <cbc:InvoicedQuantity unitCode="{unit_code}">{cantidad}</cbc:InvoicedQuantity>
            <cbc:LineExtensionAmount currencyID="{tipo_moneda}">{subtotal}</cbc:LineExtensionAmount>
            <cac:PricingReference>
                <cac:AlternativeConditionPrice>
                    <cbc:PriceAmount currencyID="{tipo_moneda}">{monto_total}</cbc:PriceAmount>
                    <cbc:PriceTypeCode>{price_type_code}</cbc:PriceTypeCode>
                </cac:AlternativeConditionPrice>
            </cac:PricingReference>
            <cac:TaxTotal>
                <cbc:TaxAmount currencyID="{tipo_moneda}">{monto_igv}</cbc:TaxAmount>
                <cac:TaxSubtotal>
                    <cbc:TaxableAmount currencyID="{tipo_moneda}">{subtotal}</cbc:TaxableAmount>
                    <cbc:TaxAmount currencyID="{tipo_moneda}">{monto_igv}</cbc:TaxAmount>
                    <cac:TaxCategory>
                        <cbc:Percent>{tax_igv_percent}</cbc:Percent>
                        {xml_afecto_tributo}
                    </cac:TaxCategory>
                </cac:TaxSubtotal>
            </cac:TaxTotal>
            <cac:Item>
                <cbc:Description>{descripcion}</cbc:Description>
            </cac:Item>
            <cac:Price>
                <cbc:PriceAmount currencyID="{tipo_moneda}">{monto_total}</cbc:PriceAmount>
            </cac:Price>
        </cac:InvoiceLine>
    """

    igv_percentage = productos.get("monto_igv", "0")
    igv_decimal = float(igv_percentage) / 100
    items = productos.get("details", [])
    xml_productos = []

    for i, producto in enumerate(items):
        subtotal_val = float(producto.get("subtotal", 0))
        xml_producto = fragmento_xml_base.format(
            id_producto=i + 1,
            cantidad=producto.get("quantity", ""),
            subtotal=subtotal_val,
            monto_total=producto.get("monto_total", ""),
            descripcion=producto.get("description", ""),
            unit_code=UNIT_CODE_NIU,
            tipo_moneda=CURRENCY_PEN,
            price_type_code=PRICE_TYPE_CODE_MAIN,
            monto_igv=str(igv_decimal * subtotal_val),
            tax_igv_percent=igv_percentage,
            xml_afecto_tributo=xml_afecto_tributo
        )
        xml_productos.append(xml_producto)

    return xml_string.replace(PLACEHOLDER_DETALLE_PRODUCTOS, "".join(xml_productos))


def _complete_credit_debit_note_details(xml_string: str, data: Dict[str, Any]) -> str:
    """Completa los detalles para una Nota de Crédito o Débito."""
    etag = "CreditNoteLine" if data.get("document_type") == "07" else "DebitNoteLine"
    etagQuantity = "CreditedQuantity" if data.get("document_type") == "07" else "DebitedQuantity"
    fragmento_xml_base = f'''
        <cac:{etag}>
            <cbc:ID>{{index}}</cbc:ID>
            <cbc:{etagQuantity} unitCode="{UNIT_CODE_NIU}">{{quantity}}</cbc:{etagQuantity}>
            <cbc:LineExtensionAmount currencyID="{CURRENCY_PEN}">{{unit_price}}</cbc:LineExtensionAmount>
            <cac:PricingReference>
                <cac:AlternativeConditionPrice>
                    <cbc:PriceAmount currencyID="{CURRENCY_PEN}">{{monto_total}}</cbc:PriceAmount>
                    <cbc:PriceTypeCode>{PRICE_TYPE_CODE_MAIN}</cbc:PriceTypeCode>
                </cac:AlternativeConditionPrice>
            </cac:PricingReference>
            <cac:TaxTotal>
                <cbc:TaxAmount currencyID="{CURRENCY_PEN}">{{monto_igv_dec}}</cbc:TaxAmount>
                <cac:TaxSubtotal>
                    <cbc:TaxableAmount currencyID="{CURRENCY_PEN}">{{unit_price}}</cbc:TaxableAmount>
                    <cbc:TaxAmount currencyID="{CURRENCY_PEN}">{{monto_igv_dec}}</cbc:TaxAmount>
                    <cac:TaxCategory>
                        <cbc:Percent>{{monto_igv}}</cbc:Percent>
                        <cbc:TaxExemptionReasonCode>10</cbc:TaxExemptionReasonCode>
                        <cac:TaxScheme>
                            <cbc:ID>1000</cbc:ID>
                            <cbc:Name>{TAX_NAME_IGV}</cbc:Name>
                            <cbc:TaxTypeCode>{TAX_TYPE_CODE_VAT}</cbc:TaxTypeCode>
                        </cac:TaxScheme>
                    </cac:TaxCategory>
                </cac:TaxSubtotal>
            </cac:TaxTotal>
            <cac:Item>
                <cbc:Description>{{descripcion}}</cbc:Description>
            </cac:Item>
            <cac:Price>
                <cbc:PriceAmount currencyID="{CURRENCY_PEN}">{{unit_price}}</cbc:PriceAmount>
            </cac:Price>
        </cac:{etag}>
    '''

    items = data.get("details", [])
    if not items:
        return xml_string

    xml_lines = []
    igv_dec = float(data.get("monto_igv", "0")) / 100

    for i, producto in enumerate(items):
        unit_price_val = float(producto.get("unit_price", 0))
        xml_line = fragmento_xml_base.format(
            index=i + 1,
            monto_igv_dec=str(igv_dec * unit_price_val),
            monto_igv=data.get("monto_igv", "0"),
            quantity=producto.get("quantity", ""),
            unit_price=unit_price_val,
            monto_total=producto.get("monto_total", ""),
            descripcion=producto.get("description", "")
        )
        xml_lines.append(xml_line)

    return xml_string.replace(PLACEHOLDER_DETALLE_PRODUCTOS_NC_ND, "".join(xml_lines))


def _complete_note_specific_data(xml_string: str, data: Dict[str, Any], invoice_relative: Dict[str, Any]) -> str:
    """Completa los campos específicos de las notas de crédito/débito."""
    if not invoice_relative:
        raise ValueError(
            "Datos de la factura relacionada no fueron proporcionados para generar la nota.")

    serie_num_relative = f"{invoice_relative.get('serie')}-{str(invoice_relative.get('num_invoice')).zfill(8)}"

    replacements = {
        PLACEHOLDER_OBSERVACION: build_note_amount_text(
            data.get("monto_total", "0"), "SOLES"),
        PLACEHOLDER_CODIGO_TABLA: data.get("codigo_table", ""),
        PLACEHOLDER_CODIGO_MENSAJE_TABLA: data.get("codigo_mensaje_table", ""),
        PLACEHOLDER_DOCUMENTO_REFERENCIADO: serie_num_relative,
        PLACEHOLDER_TIPO_DOCUMENTO_REFERENCIADO: str(
            invoice_relative.get("document_type", "")).zfill(2),
    }

    for placeholder, value in replacements.items():
        xml_string = xml_string.replace(placeholder, value)

    return _complete_credit_debit_note_details(xml_string, data)


# --- Main Orchestration Function ---

def complete_data_xml(
    data: Dict[str, Any],
    payload_customers: List[Dict[str, Any]],
    catalog_07: Optional[Dict[str, Any]] = None,
    invoice_relative: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    Completa la plantilla XML con los datos proporcionados.

    Args:
        data: Datos principales del documento.
        payload_customers: Datos del emisor y cliente.
        catalog_07: Datos del catálogo 07, requerido para facturas/boletas.
        invoice_relative: Datos de la factura relacionada, requerido para notas.

    Returns:
        El XML completado y el número de serie del documento.
    """
    try:
        document_type = data.get("document_type")
        if not document_type:
            raise ValueError("El tipo de documento es requerido.")

        xml_string = _get_xml_template(document_type)

        # --- Completar datos de cliente y emisor ---
        xml_string = _complete_customer_data(
            xml_string, payload_customers, document_type)

        # --- Completar datos generales ---
        now = datetime.now()
        serie_num_raw = data.get("document", "")
        serie_parts = serie_num_raw.split("-")
        serie_num = f"{serie_parts[0]}-{int(serie_parts[1]):08d}"

        monto_igv = data.get("monto_igv", "0")
        subtotal = str(data.get("subtotal", "0"))
        monto_total = data.get("monto_total", "0")

        replacements = {
            PLACEHOLDER_FECHA: now.strftime("%Y-%m-%d"),
            PLACEHOLDER_HORA: now.strftime("%H:%M:%S"),
            PLACEHOLDER_SERIE: serie_num,
            PLACEHOLDER_TIPO_MONEDA: CURRENCY_PEN,
            PLACEHOLDER_TIPO_DOCUMENTO: document_type,
            PLACEHOLDER_MONTO_TOTAL: monto_total,
            PLACEHOLDER_SUBTOTAL: subtotal,
            PLACEHOLDER_MONTO_IGV: str(
                float(monto_igv) / 100) if monto_igv else "0",
        }

        # print(f"Reemplazos: {replacements}")
        for placeholder, value in replacements.items():
            xml_string = xml_string.replace(placeholder, value)

        # --- Completar detalles específicos del documento ---
        if document_type in ["01", "03"]:
            if "details" in data: # details == products
                if not catalog_07:
                    raise ValueError(
                        f"Datos del catálogo {CATALOG_07_IGV} son requeridos para este tipo de documento.")
                xml_string = _complete_product_details(
                    xml_string, data, catalog_07)
        elif document_type in ["07", "08"]:
            if not invoice_relative:
                raise ValueError(
                    "La información de la factura relacionada es requerida para notas.")
            xml_string = _complete_note_specific_data(
                xml_string, data, invoice_relative)
        print(f"XML generado: {xml_string}...")  # Log the first 100 characters for debugging
        return xml_string, serie_num

    except (ValueError, KeyError, TypeError) as e:
        # Aquí se podría registrar el error con más detalle si se usara un logger
        print(f"❌ Error al generar el XML: {e}")
        raise  # Re-lanzar la excepción para que el llamador la maneje
