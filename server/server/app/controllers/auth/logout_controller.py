# """
# Controlador de cierre de sesión
# """

# from flask_restx import Resource
# from . import auth_ns
# from services.auth_service import AuthService


# @auth_ns.route('/logout')
# class Logout(Resource):
#     @auth_ns.response(200, 'Sesión cerrada exitosamente')
#     @auth_ns.response(500, 'Error en el servidor')
#     def post(self):
#         """Cerrar sesión y eliminar cookie"""
#         try:
#             return AuthService.logout_user()
#         except Exception as e:
#             return {'error': 'Error al cerrar sesión'}, 500