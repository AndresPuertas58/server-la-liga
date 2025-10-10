from flask import Flask
from flask_cors import CORS
from app.utils.database import db
from app.utils.logger import setup_logger

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuración desde archivo .env
    app.config.from_pyfile('../.env')
    app.config['DEBUG'] = True  # Para desarrollo
    
    # Inicializar base de datos
    db.init_app(app)
    
    # Configurar logger
    setup_logger(app)
    
    # Registrar blueprints
    from app.controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    return app