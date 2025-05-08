from app import create_app, db
from app.utils.batch import cargarBatch

app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Esto asegura que las tablas base existan si no usas migraciones.
        cargarBatch()
    app.run(debug=True)