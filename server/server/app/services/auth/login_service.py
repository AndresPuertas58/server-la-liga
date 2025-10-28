from app.models.user_model import User
from app.utils.database import db
from app.models.owner_model import Owner
from app.models.imagen import Imagen
from app.models.player_model import Player
import bcrypt
import jwt
from flask import make_response, jsonify
from datetime import datetime, timedelta
from app.utils.config import Config

class AuthLoginService:
    @staticmethod
    def login_user(data):
        try:
            print("🔍 Buscando usuario...")
            user = User.query.filter_by(email=data['email']).first()
            if not user:
                return make_response(jsonify({'message': 'El email ingresado no está registrado'}), 401)

            print("🔐 Verificando contraseña...")
            input_pw = data['password'].encode('utf-8')
            stored_pw = user.password.encode('utf-8')

            if not bcrypt.checkpw(input_pw, stored_pw):
                return make_response(jsonify({'message': 'La contraseña es incorrecta'}), 401)

            print(f"🎭 Role detectado: {user.role}")  # Cambié .value por .role directo

            # Generar JWT
            payload = {
                'id': user.id,
                'role': user.role,  # Cambié .value por .role directo
                'exp': datetime.utcnow() + timedelta(days=1)
            }
            token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

            # Preparar respuesta
            print("📦 Generando respuesta JSON...")
            response = make_response(jsonify({
                'message': 'Inicio de sesión exitoso',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name_user': user.name_user,
                    'fotoPerfil': user.urlphotoperfil
                }
            }))
            
            response.set_cookie(
                'liga_token',
                token,
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age=86400
            )

            print("✅ Login exitoso.")
            return response

        except Exception as e:
            print("❌ Error durante el login:", str(e))
            return make_response(jsonify({'message': 'Error interno del servidor'}), 500)