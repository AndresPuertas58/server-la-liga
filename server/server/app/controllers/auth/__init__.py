"""
Módulo de autenticación
Gestiona registro, login, logout y verificación de sesiones
"""

from flask_restx import Namespace, fields

# 📦 Crear namespace
auth_ns = Namespace('auth', description='Operaciones de autenticación')

# 🎯 Modelos para Swagger
register_model = auth_ns.model('Register', {
    'name': fields.String(required=True, example='Juan Pérez'),
    'email': fields.String(required=True, example='user@example.com'),
    'password': fields.String(required=True, example='securepassword123')
    # 'role' y 'terms' se eliminaron
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, example='user@example.com'),
    'password': fields.String(required=True, example='securepassword123')
})

# 📥 Importar controladores (esto registra las rutas automáticamente)
from .register_controller import Register
from .login_controller import Login
# from .logout_controller import Logout
# from .check_controller import CheckSession

# 📤 Exportar lo necesario
__all__ = [
    'auth_ns',
    'register_model',
    'login_model',
    'Register',
    'Login',
    'Logout',
    'CheckSession'
]