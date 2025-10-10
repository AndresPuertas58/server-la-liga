# """
# Controlador de verificación de sesión
# """

# from flask_restx import Resource
# from . import auth_ns
# from services.auth_service import AuthService


# @auth_ns.route('/check-session')
# class CheckSession(Resource):
#     @auth_ns.response(200, 'Sesión válida')
#     @auth_ns.response(401, 'Token inválido o expirado')
#     @auth_ns.response(500, 'Error en el servidor')
#     def get(self):
#         """Verificar si la sesión está activa"""
#         try:
#             return AuthService.check_session()
#         except Exception as e:
#             return {'error': 'Error al verificar sesión'}, 500