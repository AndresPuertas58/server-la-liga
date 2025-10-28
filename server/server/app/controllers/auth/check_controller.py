"""
Controlador de verificación de sesión
"""

from flask_restx import Resource
from app.controllers.auth import auth_ns
from app.services.auth.check_service import AuthService


@auth_ns.route('/check-session')
class CheckSession(Resource):
    @auth_ns.response(200, 'Sesión válida', auth_ns.models['CheckSessionSuccess'])
    @auth_ns.response(401, 'Token inválido o expirado', auth_ns.models['CheckSessionError'])
    @auth_ns.response(401, 'No autenticado', auth_ns.models['CheckSessionUnauthorized'])
    @auth_ns.response(500, 'Error en el servidor', auth_ns.models['ServerError'])
    @auth_ns.doc(description='''
        Verifica si la sesión del usuario está activa y válida.
        Requiere que el token JWT esté presente en las cookies como 'liga_token'.
        
        Respuestas:
        - 200: Sesión válida, retorna datos del token
        - 401: No autenticado (token faltante, expirado o inválido)
        - 500: Error interno del servidor
    ''')
    def get(self):
        """Verificar si la sesión está activa"""
        print("\n=== Iniciando verificación de sesión ===")
        try:
            # El servicio retorna (data, status_code)
            response_data, status_code = AuthService.check_session()
            print(f"✅ Respuesta de check_session - Status: {status_code}, Data: {response_data}")
            print("=== Fin de verificación de sesión ===\n")
            
            # Retornar la respuesta exacta del servicio
            return response_data, status_code
            
        except Exception as e:
            print("💥 Error inesperado en el controlador:", str(e))
            print("=== Fin de verificación con error ===\n")
            return {'error': 'Error al verificar sesión'}, 500