INVOICE_TEMPLATE = """
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

CREDIT_NOTE_TEMPLATE = """
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
    <cbc:Note languageLocaleID="1000">_<![CDATA[@observacion]]></cbc:Note>
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

DEBIT_NOTE_TEMPLATE = """
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
    <cbc:Note languageLocaleID="1000">_<![CDATA[@observacion]]></cbc:Note>
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