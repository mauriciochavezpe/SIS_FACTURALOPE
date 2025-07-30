"""
Este módulo define las rutas (endpoints) para la API de facturas.
Actúa como el orquestador principal para los flujos de negocio, coordinando
las llamadas a la capa de servicio (base de datos) y a los clientes externos (SUNAT).
"""

from flask import Blueprint, jsonify, request

from app import db
from app.services.invoice_service import (
    InvoiceCreationError, InvoiceNotFoundError, create_invoice_in_db,
    get_all_invoices, get_details_by_invoice, update_invoice_status)
from app.utils.sunat_client import SunatClientError, send_invoice_data_to_sunat

invoice_blueprint = Blueprint('invoices', __name__)


@invoice_blueprint.route('/', methods=['GET'])
def get_all_invoices_route():
    """Obtiene todas las facturas, con opción de filtrado."""
    try:
        filters = request.args.to_dict()
        invoices = get_all_invoices(filters)
        return jsonify({
            'status': 'success',
            'data': invoices,
            'count': len(invoices)
        }), 200
    except Exception as e:
        # Log a nivel de servidor
        print(f"Error inesperado en get_all_invoices_route: {e}")
        return jsonify({'error': 'Ocurrió un error inesperado en el servidor.'}), 500


@invoice_blueprint.route('/details/<int:id>', methods=['GET'])
def get_details_by_invoice_route(id):
    """Obtiene los detalles completos de una factura específica."""
    try:
        invoice_details = get_details_by_invoice(id)
        return jsonify(invoice_details), 200
    except InvoiceNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"Error inesperado en get_details_by_invoice_route: {e}")
        return jsonify({'error': 'Ocurrió un error inesperado en el servidor.'}), 500


@invoice_blueprint.route('/send-to-sunat', methods=['POST'])
def create_and_send_invoice_route():
    """
    Orquesta el flujo completo: crea una factura en la BD, la envía a SUNAT,
    y actualiza su estado. Es transaccional.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos en la solicitud."}), 400

    try:
        # Paso 1: Crear la factura en la base de datos (sin commit)
        # Esta función ahora devuelve el objeto Invoice, no una tupla
        invoice_obj = create_invoice_in_db(data)
        # print(f"Factura creada en BD: {invoice_obj.id}")
        # Paso 2: Enviar los datos a SUNAT
        # Esta función puede lanzar SunatClientError
        cdr_response = send_invoice_data_to_sunat(data)

        # Paso 3: Actualizar el estado de la factura con la respuesta del CDR
        # El código de estado "0" usualmente significa aceptado por SUNAT
        status_value = cdr_response.get("codigo_estado", "-1") # -1 si no hay código
        print(f"Estado de SUNAT: {status_value}")
        update_invoice_status(data["document"], status_value, cdr_response)

        # Paso 4: Si todo fue exitoso, hacer commit de la transacción
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Factura creada y enviada a SUNAT exitosamente.",
            "invoice_id": invoice_obj.id,
            "sunat_response": cdr_response
        }), 201

    except (InvoiceCreationError, SunatClientError, InvoiceNotFoundError) as e:
        # Errores de negocio o comunicación conocidos
        db.session.rollback()  # Revertir cualquier cambio en la BD
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        # Errores inesperados (ej. fallo de conexión a la BD)
        db.session.rollback()
        print(f"Error crítico en create_and_send_invoice_route: {e}") # Log para depuración
        return jsonify({"error": "Ocurrió un error interno inesperado."}), 500
