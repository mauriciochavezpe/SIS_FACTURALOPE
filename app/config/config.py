class Config:
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost:5432/Facturacion'
    SQLALCHEMY_DATABASE_URI='postgres://postgres.uukguxgscqxrajsgdrqi:Ie8yL1W8sDWRgimN@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require'


    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SECRET_KEY = "your_secret_key_here"  # Cambia por una clave segura
    JWT_SECRET_KEY = "your_jwt_secret_key_here"  # Clave para JWT
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # Tiempo de expiración en segundos
    Folder_root = "1cuYJVHk9uunJ0Z-oAnHl6BBZAo7cZVrV"


    # Configuraciones de Supabase para el cliente
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres.uukguxgscqxrajsgdrqi:Ie8yL1W8sDWRgimN@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de JWT
    JWT_SECRET_KEY = "1gK1MlaYJzI/8PS6zctzFFzru91u4XQfgEPATUozfL2agHFSReqqpoQ60eCJbU1tGyHimVRJvmeLNLxE6HmIxA=="
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    
    # Configuración de Supabase
    SUPABASE_URL = "https://uukguxgscqxrajsgdrqi.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1a2d1eGdzY3F4cmFqc2dkcnFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDczNTE4NzMsImV4cCI6MjA2MjkyNzg3M30.DyFnh1ZtAfOnN4-lIKAXks3ShjlNJctGQwEoLytgAQg"
    SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1a2d1eGdzY3F4cmFqc2dkcnFpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzM1MTg3MywiZXhwIjoyMDYyOTI3ODczfQ.eOyp0_6ASzwt0j4EL7KdGK_O_jj5cKt23_Dt3oVlqJU"
    
    # Configuración de almacenamiento
    FOLDER_ROOT = "1cuYJVHk9uunJ0Z-oAnHl6BBZAo7cZVrV"
    
    # Configuración de la base de datos (opcional, para referencia)
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = "Ie8yL1W8sDWRgimN"
    POSTGRES_HOST = "db.uukguxgscqxrajsgdrqi.supabase.co"
    POSTGRES_DATABASE = "postgres"
    # SUPABASE_URL = "https://uukguxgscqxrajsgdrqi.supabase.co"
    # SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1a2d1eGdzY3F4cmFqc2dkcnFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDczNTE4NzMsImV4cCI6MjA2MjkyNzg3M30.DyFnh1ZtAfOnN4-lIKAXks3ShjlNJctGQwEoLytgAQg"
    