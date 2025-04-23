class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost:5432/Facturacion'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SECRET_KEY = "your_secret_key_here"  # Cambia por una clave segura
    JWT_SECRET_KEY = "your_jwt_secret_key_here"  # Clave para JWT
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # Tiempo de expiración en segundos
    Folder_root = "1cuYJVHk9uunJ0Z-oAnHl6BBZAo7cZVrV"