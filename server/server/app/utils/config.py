import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    # Database Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secreto')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')  # Se leerá desde .env
    DB_NAME = os.getenv('DB_NAME', 'liga_agil_db')
    
    # Construir DATABASE_URI escapando caracteres especiales
    DATABASE_URI = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
