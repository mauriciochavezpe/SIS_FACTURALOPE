from app import create_app, db
from app.utils.batch import cargarBatch
from flask_cors import CORS
from app.config.certificado import obtener_certificado

app = create_app()
CORS(app,resources={r"/*": {"origins": "*"}})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Esto asegura que las tablas base existan si no usas migraciones.
        # cargarBatch()
        obtener_certificado()
        # generar_xml()
    app.run(debug=True, port=5000)
