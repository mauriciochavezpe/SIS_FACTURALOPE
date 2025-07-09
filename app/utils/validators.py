import requests
import os
def validar_ruc(ruc):
    try:
        """
        Valida el RUC peruano.
        
        Args:
            ruc (str): RUC a validar.
            
        Returns:
            bool: True si el RUC es válido, False en caso contrario.
        """
        url_request = os.getenv("VALIDAR_RUC_SUNAT")
        url_request = url_request.replace("XXXXX", ruc)
    
        response = requests.get(url_request, timeout=10)
        payload = response.json()
        # print("payload",payload)
        if("error" in payload):
            print("❌ Error al validar RUC:", payload["error"])
            # return {"error": payload["error"]}, 500
            raise ValueError(payload["error"])
        else:
            cliente = payload.get("lista", [])
            # quitar los espacios en blanco
            if cliente and isinstance(cliente[0], dict):
                cliente[0] = {k: v.strip() if isinstance(v, str) else v for k, v in cliente[0].items()}
            return cliente
    # return response
    except Exception as e:
        print(f"❌ Error al validar RUC: {e}")
        return {"error": str(e)}, 500

def agregar_datos_ruc_generico(xml_string, ruc, sufijo=""):
    """
    Reemplaza los placeholders de datos de RUC en el XML.
    Si sufijo es '', reemplaza los del emisor; si es '1', los del cliente.
    """
    try:
        payload = validar_ruc(ruc)
        if not payload or not isinstance(payload, list) or len(payload) == 0:
            return {"error": "RUC no encontrado o inválido"}, 404
        item = payload[0]
        # Ajustar los nombres de los campos según el payload real
        campos = [
            ("@razon_social" + sufijo,  item.get("apenomdenunciado", "")),
            ("@direccion" + sufijo,  item.get("direstablecimiento", "")),
            ("@distrito" + sufijo,  item.get("desdistrito", "")),
            ("@provincia" + sufijo, item.get("desprovincia", "")),
            ("@departamento" + sufijo, item.get("desdepartamento", "")),
        ]
        for placeholder, valor in campos:
            xml_string = xml_string.replace(placeholder, valor if valor is not None else "")
        xml_string = xml_string.replace("@ruc" + sufijo, ruc)
        return xml_string
    except Exception as e:
        print(f"❌ Error al agregar datos del RUC: {e}")
        return {"error": str(e)}, 500

# Compatibilidad con nombres anteriores
def agregar_datos_ruc(xml_string, ruc):
    return agregar_datos_ruc_generico(xml_string, ruc, sufijo="")
