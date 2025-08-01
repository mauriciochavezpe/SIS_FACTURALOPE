from decimal import Decimal
from typing import Any, Dict, List
from sqlalchemy.orm import joinedload
from app import db

from app.models.entities.Invoice import Invoice
from app.models.entities.Product import Product
from app.models.entities.InvoiceDetails import InvoiceDetail
from app.schemas.custom_detail_by_invoice_schema import InvoiceWithDetailsSchema
from app.schemas.invoice_schema import InvoiceSchema
from datetime import datetime
from flask import request
from app.utils.catalog_manager import catalog_manager
from app.utils.utils_constantes import Constantes

class InvoiceCreationError(Exception):
    """Excepción personalizada para errores durante la creación de facturas."""
    pass


class InvoiceNotFoundError(Exception):
    """Excepción para cuando una factura no se encuentra en la base de datos."""
    pass


def get_all_invoices(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Obtiene todas las facturas, opcionalmente aplicando filtros."""
    query = db.session.query(Invoice)
    if filters:
        for key, value in filters.items():
            if hasattr(Invoice, key) and value.strip("'") != '':
                query = query.filter(getattr(Invoice, key) == value.strip("'"))

    results = query.all()
    schema = InvoiceWithDetailsSchema(session=db.session, many=True)
    return schema.dump(results)


 
def get_invoice_by_serie_num(serie_num: str) -> tuple[dict[str, Any], int]:
    """Obtiene una factura por su serie y número."""
    try:
        if "-" not in serie_num:
            raise ValueError("Formato de serie inválido. Se esperaba 'SERIE-NUMERO'.")

        serie, numero_str = serie_num.split("-")
        correlativo = int(numero_str)
        num_invoice_padded = f"{correlativo:08d}"
        invoice = Invoice.query.filter_by(
            serie=serie, num_invoice=num_invoice_padded).first()

        if not invoice:
            raise InvoiceNotFoundError(f"Factura no encontrada: {serie_num}")

        print(f"Datos obtenidos: {invoice}")
        schema = InvoiceSchema(session=db.session)
        return schema.dump(invoice), 200

    except (ValueError, InvoiceNotFoundError) as e:
        return {"error": str(e)}, 404
    except Exception as e:
        # Log a more detailed error message for debugging
        print(f"Error inesperado en get_invoice_by_serie_num: {e}")
        return {"error": "Ocurrió un error inesperado al obtener la factura."}, 500

def get_details_by_invoice(invoice_id: int) -> Dict[str, Any]:
    """Obtiene los detalles completos de una factura, incluyendo sus productos."""
    invoice = db.session.query(Invoice).options(joinedload(Invoice.invoice_details).joinedload(InvoiceDetail.product).joinedload(Product.category)).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise InvoiceNotFoundError(f"Factura con ID {invoice_id} no encontrada.")

    schema = InvoiceWithDetailsSchema(session=db.session)
    result = schema.dump(invoice),200
    return result


def create_invoice_in_db(data: Dict[str, Any]) -> Invoice:
    """
    Crea una factura y sus detalles en la base de datos pero no hace commit.
    La responsabilidad del commit se delega al orquestador de la ruta.
    """
    try:
        documento = data.get("document", "")
        if "-" not in documento:
            raise InvoiceCreationError(
                "Formato de documento inválido. Debe ser 'SERIE-NUMERO'.")

        serie, numero_str = documento.split("-")
        correlativo = int(numero_str)

        pending_status_id = catalog_manager.get_id(Constantes.CATALOG_CATEGORY_STATUS, Constantes.STATUS_PENDING)

        # Crear la cabecera de la factura
        invoice = Invoice(
            customer_id=data.get("customer_id"),
            num_invoice=f"{correlativo:08d}",
            serie=serie,
            related_invoice_id=data.get("related_invoice_id",None),
            document_type=data.get("document_type"),
            date=data.get("date"),
            id_status=pending_status_id,
            subtotal=Decimal(data.get("subtotal", 0) or 0),
            total=Decimal(data.get("monto_total", 0) or 0),
            tax=Decimal(data.get("monto_igv", 0) or 0),
            createdAt = datetime.now(),
            createdBy = request.headers.get("user", "system"),
            ip = request.remote_addr
        )
        db.session.add(invoice)
        db.session.flush()  # Para obtener el ID de la factura para los detalles

        # Crear los detalles de la factura
        detalles_data = data.get("details", [])
        if not detalles_data:
            raise InvoiceCreationError(
                "Debe proporcionar al menos un detalle de factura.")

        for item in detalles_data:
            detalle = InvoiceDetail(
                invoice_id=invoice.id,
                product_id=item["product_id"],
                quantity=Decimal(item.get("quantity", 1)),
                unit_price=Decimal(item.get("unit_price", 0)),
                discount=Decimal(item.get("discount", 0)),
                subtotal=Decimal(item.get("subtotal", 0)),
                tax=Decimal(item.get("tax", 0)),
                total=Decimal(item.get("monto_total", 0)),
                createdAt = datetime.now(),
                createdBy = request.headers.get("user", "system"),
                ip = request.remote_addr
            )
            db.session.add(detalle)
        return invoice

    except (KeyError, TypeError, ValueError) as e:
        raise InvoiceCreationError(f"Datos de factura inválidos: {e}")


def update_invoice_status(documento: str, status_value: str, cdr_data: Dict[str, Any] = None):
    """
    Actualiza el estado de una factura después de la respuesta de SUNAT.
    """
    serie, numero_str = documento.split("-")
    correlativo = int(numero_str)
    num_invoice_padded = f"{correlativo:08d}"

    invoice = Invoice.query.filter_by(
        serie=serie, num_invoice=num_invoice_padded).first()
    if not invoice:
        raise InvoiceNotFoundError(f"Factura no encontrada: {documento}")

    status_id = catalog_manager.get_id(Constantes.CATALOG_INVOICE_STATUS, Constantes.STATUS_SENT_SUNAT)

    if not status_id:
        print(f"Advertencia: Valor de estado '{status_value}' no encontrado en MasterData.")
    else:
        invoice.id_status = status_id

    if cdr_data:
        invoice.sunat_response = cdr_data
    
    invoice.modifiedAt = datetime.now()
    invoice.modifiedBy = request.headers.get("user", "system")
    invoice.ip = request.remote_addr

    return invoice
