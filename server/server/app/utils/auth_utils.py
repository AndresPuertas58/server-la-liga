# app/utils/auth_utils.py
import jwt
from flask import request
from app.models.user_model import User
from app.utils.config import Config

def obtener_usuario_desde_token():
    print("🔐 Intentando obtener usuario desde token...")
    token = request.cookies.get("liga_token")
    print(f"🍪 Token encontrado en cookies: {token}")
    print(f"📋 Todas las cookies: {request.cookies}")
    
    if not token:
        print("❌ No se encontró token en las cookies")
        return None, {"error": "Usuario no autenticado"}, 401

    try:
        print("🔓 Decodificando token...")
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        print(f"📊 Token decodificado: {data}")
        
        user_id = data.get("id")
        print(f"👤 User ID desde token: {user_id}")
        
        usuario = User.query.get(user_id)
        if not usuario:
            print("❌ Usuario no encontrado en BD")
            return None, {"error": "Usuario no válido"}, 403
        
        print(f"✅ Usuario válido: {usuario.email}, Role: {usuario.role.value}")
        return usuario, None, 200
        
    except jwt.ExpiredSignatureError:
        print("❌ Token expirado")
        return None, {"error": "Token expirado"}, 401
    except jwt.InvalidTokenError as e:
        print(f"❌ Token inválido: {str(e)}")
        return None, {"error": "Token inválido"}, 401
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return None, {"error": "Error interno"}, 500