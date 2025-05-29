from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
import os
from lxml import etree
import xmlsec

def obtener_certificado(ruta_p12="assets/certificado.p12", contrasena_p12="Dino1490"):
    """
    Extrae el certificado X.509 de un archivo.p12 y lo devuelve en Base64.
    """
    path = os.path.join("assets","certificado.p12")

    with open(path, "rb") as f:
        p12_data = f.read()

    # Cargar el archivo P12
    # La contraseña debe ser bytes
    private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
        p12_data,
        contrasena_p12.encode('utf-8'), # Codificar la contraseña a bytes
        default_backend()
    )

    if certificate:
        # Serializar el certificado a formato PEM
        pem_certificate = certificate.public_bytes(serialization.Encoding.PEM)
        # Eliminar encabezados, pies de página PEM y saltos de línea, luego codificar en Base64
        # El XML espera el contenido Base64 puro del certificado
        valor_certificado = pem_certificate.decode('utf-8').replace("-----BEGIN CERTIFICATE-----", "").replace("-----END CERTIFICATE-----", "").replace("\n", "")
        return valor_certificado
    else:
        return None



def firmar_xml_con_placeholder(xml_con_placeholder):
    # Paso 1: reemplazar el marcador @firma_digital por un nodo vacío temporal
    # xml_con_placeholder = xml_con_placeholder.replace(
    #     "@firma_digital", "<placeholder_firma/>"
    # )

    # Paso 2: parsear el XML string a ElementTree
    tree = etree.fromstring(xml_con_placeholder.encode("utf-8"))
    doc = etree.ElementTree(tree)
    path_p12 = os.path.join("assets","certificado.p12")
    p12_password = "Dino1490"
    # Paso 3: cargar certificado .p12
    with open(path_p12, 'rb') as f:
        pfx_data = f.read()
    private_key, cert, _ = pkcs12.load_key_and_certificates(
        pfx_data, p12_password.encode('utf-8'),
        default_backend()
    )

    # Paso 4: buscar el nodo donde se debe insertar la firma
    ns = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    }
    extension_content = doc.find(".//ext:ExtensionContent", namespaces=ns)
    # placeholder = extension_content.find("<placeholder_firma/>")
    # if placeholder is not None:
    #     extension_content.remove(placeholder)

    # Paso 5: crear nodo de firma
    signature_node = xmlsec.template.create(
        tree,
        xmlsec.Transform.EXCL_C14N,
        xmlsec.Transform.RSA_SHA1,
        ns="ds"
    )
    print("signature_node",str(signature_node))
    extension_content.append(signature_node)

    # Configurar transformaciones y referencia
    ref = xmlsec.template.add_reference(signature_node, xmlsec.Transform.SHA1)
    xmlsec.template.add_transform(ref, xmlsec.Transform.ENVELOPED)
    key_info = xmlsec.template.ensure_key_info(signature_node)
    xmlsec.template.add_x509_data(key_info)

    # Paso 6: firmar
    # Crear contexto de firma
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)    
    # Cargar clave privada desde certificado
    key = xmlsec.Key.from_memory(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ),
        xmlsec.KeyFormat.PEM,
        None
    )

    # Cargar certificado en la clave
    key.load_cert_from_memory(cert_pem, xmlsec.KeyFormat.CERT_PEM)
    ctx = xmlsec.SignatureContext()
    # Asignar clave al contexto de firma
    ctx.key = key
    # Firmar el nodo de firma
    ctx.sign(signature_node)
    # Paso 7: retornar el XML final como string
    return etree.tostring(doc, pretty_print=True, encoding="utf-8", xml_declaration=True).decode()