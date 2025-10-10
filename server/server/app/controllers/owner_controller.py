# app/controllers/owner_controller.py
from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.owner_service import OwnerService
from app.utils.auth_utils import obtener_usuario_desde_token  # Usar la misma utilidad de autenticación

owner_ns = Namespace('owner', description='Operaciones para dueños')

# Modelo de perfil para Swagger
owner_profile_model = owner_ns.model('OwnerProfile', {
    'nombre_administrador': fields.String(required=True, description='Nombre completo del administrador'),
    'telefono': fields.String(required=True, description='Teléfono del administrador'),
})

# Obtener perfil por ID
@owner_ns.route('/profile/<int:user_id>')
class OwnerProfileById(Resource):
    def get(self, user_id):
        """Obtener perfil de dueño por ID"""
        result = OwnerService.get_owner_profile(user_id)
        return result, 200

# Perfil del dueño logueado (GET y POST)
@owner_ns.route('/profile-owner')
class OwnerProfile(Resource):
    @owner_ns.expect(owner_profile_model)
    def post(self):
        """Crear o completar el perfil del dueño logueado"""
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        # Verificar que el usuario es un dueño
        if usuario.role.value != 'owner':
            return {'message': 'Solo dueños pueden completar este perfil'}, 403

        data = request.get_json()
        if not data:
            return {'message': 'Datos inválidos'}, 400

        # Llamada al servicio para crear/actualizar perfil
        try:
            result = OwnerService.create_owner_profile(usuario.id, data)
            return result, 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500

    def get(self):
        """Obtener perfil del dueño logueado"""
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        # Verificar que el usuario es un dueño
        if usuario.role.value != 'owner':
            return {'message': 'Solo dueños pueden acceder a este perfil'}, 403

        try:
            result = OwnerService.get_owner_profile(usuario.id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 404