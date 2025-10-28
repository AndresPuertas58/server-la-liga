# import os
# import logging
# import traceback
# from dotenv import load_dotenv

# from flask import Flask, jsonify
# from flask_restx import Api
# from flask_cors import CORS
# from flask_session import Session
# from werkzeug.exceptions import HTTPException, BadRequest

# from app.utils.database import db

# # Cargar variables de entorno
# load_dotenv()

# def create_app():
#     # Configuración básica de logging
#     logging.basicConfig(level=logging.DEBUG)
    
#     # Crear aplicación Flask
#     app = Flask(__name__)
    
#     # Configuración de la aplicación
#     configure_app(app)
    
#     # Inicializar extensiones
#     initialize_extensions(app)
    
#     # Configurar API
#     api = configure_api(app)
    
#     # Registrar namespaces
#     register_namespaces(api)
    
#     # Configurar manejo de errores
#     configure_error_handlers(app)
    
#     return app


# def configure_app(app):
#     """Configura las variables de la aplicación Flask"""
    
#     # Configuración de la base de datos
#     app.config['SQLALCHEMY_DATABASE_URI'] = (
#         f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@'
#         f'{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
#     )
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key')
    
#     # Configuración de sesión
#     app.config['SESSION_TYPE'] = 'filesystem'
#     app.config['SESSION_PERMANENT'] = False
#     app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
#     app.config['SESSION_COOKIE_SECURE'] = False


# def initialize_extensions(app):
#     """Inicializa todas las extensiones de Flask"""
    
#     # Configurar CORS
#     CORS(app,
#         resources={
#             r"/*": {
#                 "origins": [
#                     "https://www.vetlink.pet",
#                     "http://localhost:3000",
#                     "http://localhost:3001",
#                     "http://localhost:4000"
#                 ],
#                 "supports_credentials": True,
#                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
#                 "allow_headers": "*"
#             }
#         }
#     )
    
#     # Inicializar sesiones
#     Session(app)
    
#     # Inicializar base de datos
#     db.init_app(app)


# def configure_api(app):
#     """Configura Flask-RESTX API con Swagger"""
    
#     api = Api(
#         app, 
#         title="Liga Ágil API", 
#         version="1.0",
#         description="API para la gestión de ligas deportivas",
#         doc="/docs/"  # Ruta para la documentación Swagger
#     )
    
#     return api


# def register_namespaces(api):
#     """Registra todos los namespaces de la API"""
    
#     from app.controllers.auth_controller import auth_ns
#     from app.controllers.owner_controller import owner_ns
#     from app.controllers.cancha_controller import cancha_ns
#     from app.controllers.reserva_controller import reserva_ns
#     from app.controllers.player_controller import player_ns
#     from app.controllers.account_controller import account_ns

#     api.add_namespace(account_ns, '/account')
#     api.add_namespace(auth_ns, path='/auth')
#     api.add_namespace(owner_ns, path='/owner')
#     api.add_namespace(cancha_ns, path='/cancha')
#     api.add_namespace(reserva_ns, path="/reservas")
#     api.add_namespace(player_ns, path="/player")


# def configure_error_handlers(app):
#     """Configura el manejo personalizado de errores"""
    
#     @app.errorhandler(ValueError)
#     def handle_value_error(error):
#         return jsonify({'message': str(error)}), 400

#     @app.errorhandler(BadRequest)
#     def handle_bad_request(error):
#         return jsonify({'message': str(error.description)}), 400

#     @app.errorhandler(404)
#     def not_found(error):
#         return jsonify({'message': 'Endpoint no encontrado'}), 404

#     @app.errorhandler(500)
#     def internal_server_error(error):
#         return jsonify({'message': 'Error interno del servidor'}), 500

#     @app.errorhandler(Exception)
#     def handle_general_error(error):
#         # Manejar excepciones HTTP estándar
#         if isinstance(error, HTTPException):
#             return jsonify({'message': error.description}), error.code
        
#         # Loggear error completo para depuración
#         app.logger.error(f"Error no manejado: {str(error)}")
#         traceback.print_exc()
        
#         return jsonify({'message': 'Error inesperado en el servidor'}), 500


# # Para ejecución directa del archivo
# if __name__ == '__main__':
#     app = create_app()
#     app.run(debug=True, host='0.0.0.0', port=5050)

import os
import logging
import traceback
from dotenv import load_dotenv

from flask import Flask, jsonify
from flask_restx import Api
from flask_cors import CORS
from flask_session import Session
from werkzeug.exceptions import HTTPException, BadRequest

from app.utils.database import db

# Cargar variables de entorno
load_dotenv()

def create_app():
    # Configuración básica de logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Crear aplicación Flask
    app = Flask(__name__)
    
    # Configuración de la aplicación
    configure_app(app)
    
    # Inicializar extensiones
    initialize_extensions(app)
    
    # Configurar API
    api = configure_api(app)
    
    # Registrar namespaces
    register_namespaces(api)
    
    # Configurar manejo de errores
    configure_error_handlers(app)
    
    return app


def configure_app(app):
    """Configura las variables de la aplicación Flask"""
    
    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@'
        f'{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key')
    
    # Configuración de sesión
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False


def initialize_extensions(app):
    """Inicializa todas las extensiones de Flask"""
    
    # Configurar CORS condicional basado en el entorno
    if os.environ.get('FLASK_ENV') == 'development':
        CORS(app,
            resources={
                r"/*": {
                    "origins": [
                        "https://www.vetlink.pet",
                        "http://localhost:3000",
                        "http://localhost:3001",
                        "http://localhost:4000"
                    ],
                    "supports_credentials": True,
                    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                    "allow_headers": "*"
                }
            }
        )
        app.logger.info("CORS habilitado para entorno de desarrollo")
    else:
        app.logger.info("CORS deshabilitado para entorno de producción")
    
    # Inicializar sesiones
    Session(app)
    
    # Inicializar base de datos
    db.init_app(app)


def configure_api(app):
    """Configura Flask-RESTX API con Swagger"""
    
    api = Api(
        app, 
        title="Liga Ágil API", 
        version="1.0",
        description="API para la gestión de ligas deportivas",
        doc="/docs/"  # Ruta para la documentación Swagger
    )
    
    return api


def register_namespaces(api):
    """Registra todos los namespaces de la API"""
    
    # Importar namespaces
    from app.controllers.auth import auth_ns, player_ns, account_ns, posts_ns, cancha_ns, reserva_ns

    # Registrar namespaces
    api.add_namespace(account_ns, path='/account')
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(player_ns, path='/player')
    api.add_namespace(posts_ns, path='/posts')
    api.add_namespace(cancha_ns, path='/cancha')
    api.add_namespace(reserva_ns, path='/reserva') 
    


def configure_error_handlers(app):
    """Configura el manejo personalizado de errores"""
    
    @app.errorhandler(ValueError)
    def handle_value_error(error):
        return jsonify({'message': str(error)}), 400

    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return jsonify({'message': str(error.description)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Endpoint no encontrado'}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({'message': 'Error interno del servidor'}), 500

    @app.errorhandler(Exception)
    def handle_general_error(error):
        # Manejar excepciones HTTP estándar
        if isinstance(error, HTTPException):
            return jsonify({'message': error.description}), error.code
        
        # Loggear error completo para depuración
        app.logger.error(f"Error no manejado: {str(error)}")
        traceback.print_exc()
        
        return jsonify({'message': 'Error inesperado en el servidor'}), 500


# Para ejecución directa del archivo
if __name__ == '__main__':
    app = create_app()
    
    # Determinar entorno automáticamente si no está configurado
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'  # Por defecto desarrollo
    
    app.logger.info(f"Ejecutando en modo: {os.environ.get('FLASK_ENV')}")
    app.run(debug=True, host='0.0.0.0', port=5050)