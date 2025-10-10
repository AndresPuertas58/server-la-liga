# # from app.models.user_model import User, UserRole
# # from app.utils.database import db
# # from app.models.owner_model import Owner
# # from app.models.imagen import Imagen
# # from app.models.player_model import Player
# # import bcrypt
# # import jwt
# # from flask import make_response, jsonify, request
# # from datetime import datetime, timedelta
# # from app.utils.config import Config
# # from app.utils.auth_utils import obtener_usuario_desde_token




# # class AuthService:
# #     @staticmethod
# #     def register_user(data):
# #         # Verificar si el email ya existe
# #         if User.query.filter_by(email=data['email']).first():
# #             raise ValueError('El email ya está registrado')

# #         # Hashear la contraseña
# #         hashed_password = bcrypt.hashpw(
# #             data['password'].encode('utf-8'),
# #             bcrypt.gensalt()
# #         ).decode('utf-8')

# #         # Crear nuevo usuario
# #         user = User(
# #             email=data['email'],
# #             password=hashed_password,
# #             role=UserRole(data['role'].lower()),
# #             terms=data['terms']
# #         )
# #         db.session.add(user)
# #         db.session.commit()

# #         return {
# #             'message': 'Registro exitoso',
# #             'user': {
# #                 'id': user.id,
# #                 'email': user.email,
# #                 'role': user.role.value
# #             }
# #         }

#     @staticmethod
#     def login_user(data):
#         try:
#             print("Buscando usuario...")
#             user = User.query.filter_by(email=data['email']).first()
#             if not user:
#                 return make_response(jsonify({'message': 'El email ingresado no está registrado'}), 401)

#             print("Verificando contraseña...")
#             input_pw = data['password'].encode('utf-8')
#             stored_pw = user.password.encode('utf-8')

#             if not bcrypt.checkpw(input_pw, stored_pw):
#                 return make_response(jsonify({'message': 'La contraseña es incorrecta'}), 401)

#             nombre_completo = None
#             nombre_administrador = None
#             foto_perfil = None

#             print(f"Role detectado: {user.role.value}")

#             if user.role.value == 'owner':
#                 owner = Owner.query.filter_by(user_id=user.id).first()
#                 if owner:
#                     nombre_administrador = owner.nombre_administrador
#                 print(f"Owner: {nombre_administrador}")

#             elif user.role.value == 'player':
#                 player = Player.query.filter_by(user_id=user.id).first()
#                 print("Player encontrado:", player)
#                 if player:
#                     nombre_completo = player.nombre_completo
#                     imagen = Imagen.query.filter_by(player_id=player.id).order_by(Imagen.orden).first()
#                     if imagen:
#                         foto_perfil = imagen.url_imagen
#                 print(f"Jugador: {nombre_completo}, Imagen: {foto_perfil}")

#             # Generar JWT
#             payload = {
#                 'id': user.id,
#                 'role': user.role.value,
#                 'exp': datetime.utcnow() + timedelta(days=1)
#             }
#             token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

#             # Preparar respuesta
#             print("Generando respuesta JSON...")
#             response = make_response(jsonify({
#                 'message': 'Inicio de sesión exitoso',
#                 'user': {
#                     'id': user.id,
#                     'email': user.email,
#                     'role': user.role.value,
#                     'is_profile_completed': user.is_profile_completed,
#                     'nombreCompleto': nombre_completo,
#                     'nombreAdministrador': nombre_administrador,
#                     'fotoPerfil': foto_perfil
#                 }
#             }))

#             response.set_cookie(
#                 'liga_token',
#                 token,
#                 httponly=True,
#                 secure=True,
#                 samesite='Strict',
#                 max_age=86400
#             )

#             print("Login exitoso.")
#             return response

#         except Exception as e:
#             print("❌ Error durante el login:", str(e))
#             return make_response(jsonify({'message': 'Error interno del servidor'}), 500)


# #     @staticmethod
# #     def check_session():
# #         # Leer el token desde la cookie
        
# #         token = request.cookies.get('liga_token')
# #         print("Token recibido:", token)  # ← DEBUG
# #         if not token:
# #             return {'message': 'No autenticado'}, 401

# #         try:
# #             # Decodificar el token
# #             data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
# #             print("Datos decodificados:", data)  # ← DEBUG
# #             user = User.query.get(data['id'])

# #             if not user:
# #                 return {'message': 'Usuario no encontrado'}, 404

# #             print("Usuario autenticado:", user.email)  # ← DEBUG
# #             return jsonify({
# #                 'id': user.id,
# #                 'email': user.email,
# #                 'role': user.role.value,
# #                 'is_profile_completed': user.is_profile_completed
# #             })
        
# #         except jwt.ExpiredSignatureError:
# #             print("Token expirado")  # ← DEBUG
# #             return {'message': 'Token expirado'}, 401
# #         except jwt.InvalidTokenError:
# #              print("Token inválido")  # ← DEBUG
# #              return {'message': 'Token inválido'}, 401
# #         except Exception as e:
# #              print("Error inesperado:", str(e))  # ← DEBUG
# #              return {'message': 'Error interno en el servidor'}, 500
        


# #     @staticmethod
# #     def logout_user():
# #         response = make_response({'message': 'Sesión cerrada exitosamente'})
# #         response.set_cookie(
# #               'liga_token',
# #               '',
# #               expires=0,
# #               httponly=True,
# #               secure=True,
# #               samesite='Strict'
# #         )
# #         return response

