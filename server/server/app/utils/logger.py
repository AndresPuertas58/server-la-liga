import logging
from logging.handlers import RotatingFileHandler
import os
from flask import current_app
from app.utils.config import Config

def setup_logger(app):
    """Configura el sistema de logging para la aplicación"""
    
    # Crear directorio de logs si no existe
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar el nivel de log
    log_level = logging.INFO
    if app.config['DEBUG']:
        log_level = logging.DEBUG
    
    # Configurar el formato del log
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Configurar el handler para archivo
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'liga_agil.log'),
        maxBytes=1024 * 1024 * 10,  # 10 MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Configurar el handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Añadir handlers al logger de la app
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    # Deshabilitar el logger por defecto de Werkzeug
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    app.logger.info('Logger configurado correctamente')