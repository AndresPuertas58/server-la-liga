# app/controllers/player_controller.py
from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.player_service import PlayerService
from app.services.player_reserva_service import PlayerReservaService
from app.utils.auth_utils import obtener_usuario_desde_token  # Usar tu utilidad existente

player_ns = Namespace('player', description='Operaciones para jugadores')

# Modelo de perfil para Swagger
player_profile_model = player_ns.model('PlayerProfile', {
    'deporte': fields.String(required=True),
    'nombre_completo': fields.String(required=True),
    'fecha_nacimiento': fields.String(required=True),
    'posicion': fields.String(required=True),
    'genero': fields.String(required=True, enum=['masculino', 'femenino', 'otro']),
    'pierna_dominante': fields.String(required=True, enum=['izquierda', 'derecha', 'ambas']),
    'mano_dominante': fields.String(required=True, enum=['izquierda', 'derecha', 'ambas']),
    'altura': fields.String(required=True),
    'peso': fields.String(required=True),
    'ciudad': fields.String(required=True),
    'telefono': fields.String(required=True),
    'profilePicture': fields.List(fields.String, required=True),
})

# Obtener perfil por ID
@player_ns.route('/profile/<int:user_id>')
class PlayerProfileById(Resource):
    def get(self, user_id):
        """Obtener perfil de jugador por ID"""
        result = PlayerService.get_profile(user_id)
        return result, 200

# Perfil del jugador logueado (GET y POST)
@player_ns.route('/profile-player')
class PlayerProfile(Resource):
    @player_ns.expect(player_profile_model)
    def post(self):
        """Crear o completar el perfil del jugador logueado"""
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        # Verificar que el usuario es un jugador
        if usuario.role.value != 'player':
            return {'message': 'Solo jugadores pueden completar este perfil'}, 403

        data = request.get_json()
        if not data:
            return {'message': 'Datos inválidos'}, 400

        # Llamada al servicio para crear/actualizar perfil
        try:
            result = PlayerService.create_player_profile(usuario.id, data)
            return result, 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500

    def get(self):
        """Obtener perfil del jugador logueado"""
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        # Verificar que el usuario es un jugador
        if usuario.role.value != 'player':
            return {'message': 'Solo jugadores pueden acceder a este perfil'}, 403

        try:
            result = PlayerService.get_profile(usuario.id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 404
        
@player_ns.route('/mis-reservas')
class MisReservasController(Resource):
    def get(self):
        """Obtener todas las reservas del jugador logueado"""
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        # Verificar que el usuario es un jugador
        if usuario.role.value != 'player':
            return {'message': 'Solo jugadores pueden acceder a este recurso'}, 403

        try:
            result = PlayerReservaService.obtener_reservas_jugador(usuario.id)
            return result, 200
        except Exception as e:
            return {'error': str(e)}, 500

@player_ns.route('/mis-reservas/<int:reserva_id>')
class MisReservaController(Resource):
    def delete(self, reserva_id):
        """Cancelar una reserva específica del jugador"""
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        # Verificar que el usuario es un jugador
        if usuario.role.value != 'player':
            return {'message': 'Solo jugadores pueden acceder a este recurso'}, 403

        try:
            result = PlayerReservaService.cancelar_reserva_jugador(usuario.id, reserva_id)
            return result, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500