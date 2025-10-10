from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from app.utils.config import Config

db = SQLAlchemy()

def init_db(app):
    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }
    
    db.init_app(app)
    
    # Verificar conexión
    with app.app_context():
        try:
            db.engine.connect()
            current_app.logger.info("✅ Conexión a la base de datos exitosa!")
        except Exception as e:
            current_app.logger.error(f"❌ Error de conexión a la base de datos: {str(e)}")
            raise e