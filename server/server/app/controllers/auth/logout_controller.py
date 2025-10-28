"""
Controlador de cierre de sesión
"""

from flask_restx import Resource
from . import auth_ns
from app.services.auth.logout_service import logout_user  # ✅ Importación correcta

@auth_ns.route('/logout')
class Logout(Resource):
    @auth_ns.response(200, 'Sesión cerrada exitosamente')
    @auth_ns.response(500, 'Error en el servidor')
    def post(self):
        """Cerrar sesión y eliminar cookie"""
        try:
            return logout_user()  # ✅ Ahora es una función, no un método estático
        except Exception as e:
            return {'error': 'Error al cerrar sesión'}, 500