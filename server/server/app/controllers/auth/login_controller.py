"""
Controlador de login de usuarios
"""

from flask_restx import Resource
from . import auth_ns, login_model
# Cambia esta línea:
from app.services.auth.login_service import AuthLoginService  # ✅ Import absoluto
from app.utils.validation_utils import validate_login


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Login exitoso')
    @auth_ns.response(400, 'Error de validación')
    @auth_ns.response(401, 'Credenciales inválidas')
    @auth_ns.response(500, 'Error en el servidor')
    def post(self):
        """Iniciar sesión de usuario"""
        data = auth_ns.payload

        # Validar entrada
        errors = validate_login(data)
        if errors:
            return {'errors': errors}, 400

        try:
            result = AuthLoginService.login_user(data)
            return result
        except ValueError as e:
            return {'error': str(e)}, 401
        except Exception as e:
            return {'error': 'Error en el servidor'}, 500