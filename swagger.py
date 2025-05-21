from flask_restx import Api

api = Api(
    version='1.0',
    title='Sistema de Facturación API',
    description='API para el sistema de facturación',
    doc='/docs'  # Ruta donde se servirá la documentación
)