import os
import base64
import time
import requests

def download_file(url, dest, auth_header):
    try:
        headers = {
            "Authorization": auth_header
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        with open(dest, "wb") as f:
            f.write(response.content)
        print(f"Archivo descargado: {dest}")
    except Exception as e:
        print(f"Error al descargar el archivo {url}: {e}")
        raise

def download_wsdl_files():
    user_name = os.getenv("SUNAT_USUARIO_DUMMY")
    password = os.getenv("SUNAT_PASS_DUMMY")
    auth = "Basic " + base64.b64encode(f"{user_name}:{password}".encode()).decode()

    base_url = os.getenv("sunat_beta") # reemplaza esto por la real

    files = [
        {"url": f"{base_url}/billService?wsdl", "dest": "./app/wsdl/billService.wsdl"},
        {"url": f"{base_url}/billService?ns1.wsdl", "dest": "./app/wsdl/billService_ns1.wsdl"},
        {"url": f"{base_url}/billService.xsd2.xsd", "dest": "./app/wsdl/billService.xsd2.xsd"},
    ]

    for file in files:
        download_file(file["url"], file["dest"], auth)
        time.sleep(0.5)

if __name__ == "__main__":
    download_wsdl_files()