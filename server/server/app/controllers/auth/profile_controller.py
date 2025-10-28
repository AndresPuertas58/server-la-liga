from app.models.user_model import User
from app.utils.database import db
from datetime import datetime
from app.utils.auth_utils import obtener_usuario_desde_token
from flask import request
from flask_restx import Resource
from app.services.auth.profile_service import PlayerService

from . import player_ns, player_profile_model


# 🔹 Obtener perfil de jugador (por ID o por token si no se pasa ID)
@player_ns.route('/profile', defaults={'user_id': None})
@player_ns.route('/profile/<int:user_id>')
class PlayerProfileById(Resource):
    def get(self, user_id):
        """Obtener perfil de jugador (por ID o token JWT)"""
        # Si no se pasa user_id, obtenerlo desde el token
        if user_id is None:
            usuario, error, status_code = obtener_usuario_desde_token()
            if error:
                return error, status_code
            user_id = usuario.id
            print(f"🧩 Obtenido user_id desde token: {user_id}")

        # Llamar al servicio para obtener el perfil
        result = PlayerService.get_profile(user_id)
        return result, 200


# 🔹 Perfil del jugador logueado (GET y PUT)
@player_ns.route('/profile_user')
class PlayerProfile(Resource):
    @player_ns.expect(player_profile_model)
    def put(self):
        """Crear o completar el perfil del jugador logueado"""
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        if usuario.role != 'player':
            return {'message': 'Solo jugadores pueden completar este perfil'}, 403

        data = request.get_json()
        if not data:
            return {'message': 'Datos inválidos'}, 400

        try:
            result = PlayerService.create_player_profile(usuario.id, data)
            return result, 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500

    def get(self):
        """Obtener perfil del jugador logueado"""
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        if usuario.role != 'player':
            return {'message': 'Solo jugadores pueden acceder a este perfil'}, 403

        try:
            result = PlayerService.get_profile(usuario.id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 404
