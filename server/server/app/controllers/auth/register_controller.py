"""
Controlador de registro de usuarios
"""

from flask_restx import Resource
from . import auth_ns, register_model
# Cambia el import por:
from app.services.auth.register_service import AuthService
from app.utils.validation_utils import validate_registration


@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'Usuario registrado exitosamente')
    @auth_ns.response(400, 'Error de validación')
    @auth_ns.response(500, 'Error en el servidor')
    def post(self):
        """Registrar nuevo usuario"""
        data = auth_ns.payload

        # Validar entrada
        errors = validate_registration(data)
        if errors:
            return {'errors': errors}, 400

        try:
            result = AuthService.register_user(data)
            return result, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Error en el servidor'}, 500