from flask import request
import jwt
from app.utils.config import Config

class AuthService:
    @staticmethod
    def check_session():
        """
        Verifica la validez de la sesión del usuario mediante el token JWT
        
        Returns:
            tuple: (response_data, status_code)
        """
        print("\n=== [SERVICE] Verificación de sesión ===")

        token = request.cookies.get('liga_token')
        print("🍪 Token recibido:", token)

        if not token:
            print("❌ No se recibió token (usuario no autenticado).")
            return {
                'authenticated': False, 
                'message': 'No autenticado'
            }, 401

        try:
            # Decodificar el token JWT
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            print("✅ Token válido. Datos decodificados:", data)

            # Respuesta exitosa
            return {
                'authenticated': True,
                'message': 'Sesión válida',
                'token_data': data
            }, 200

        except jwt.ExpiredSignatureError:
            print("⌛ Token expirado")
            return {
                'authenticated': False, 
                'message': 'Token expirado'
            }, 401

        except jwt.InvalidTokenError:
            print("🚫 Token inválido")
            return {
                'authenticated': False, 
                'message': 'Token inválido'
            }, 401

        except Exception as e:
            print("💥 Error inesperado en el servicio:", str(e))
            return {
                'authenticated': False, 
                'message': 'Error interno del servidor'
            }, 500