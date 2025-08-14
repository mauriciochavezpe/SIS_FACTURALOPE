from app import create_app, db
from scripts.load_master_data import cargarBatch
from scripts.download_wsdl import download_wsdl_files

from flask_cors import CORS
from app.utils.xml_security import obtener_certificado

app = create_app()
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()  # Esto borra todas las tablas si ya existen.
        db.create_all()  # Esto asegura que las tablas base existan si no usas migraciones.
        # download_wsdl_files()
        obtener_certificado()
    app.run(debug=True, port=4041)
