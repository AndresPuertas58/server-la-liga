from flask_restx import fields
from . import player_ns

# Modelo para el perfil del jugador (para PUT)
player_profile_model = player_ns.model('PlayerProfile', {
    'telephone': fields.String(required=True, description='Teléfono del jugador'),
    'city': fields.String(required=True, description='Ciudad del jugador'),
    'sport': fields.String(required=True, description='Deporte que practica'),
    'position': fields.String(required=True, description='Posición en el deporte'),
    'biography': fields.String(description='Biografía del jugador'),
    'profilePicture': fields.String(description='URL de la foto de perfil'),
    'urlphotoperfil': fields.String(description='URL alternativa de foto de perfil')
})

# Modelo para respuesta del perfil
player_profile_response = player_ns.model('PlayerProfileResponse', {
    'message': fields.String(description='Mensaje de confirmación'),
    'user': fields.Raw(description='Datos del usuario actualizado')
})

# Modelo para respuesta de foto de perfil
profile_picture_response = player_ns.model('ProfilePictureResponse', {
    'message': fields.String(description='Mensaje de confirmación'),
    'url_imagen': fields.String(description='URL interna de la imagen'),
    'url_accesible': fields.String(description='URL accesible para el frontend')
})

# Modelo para información básica del usuario
user_basic_info_model = player_ns.model('UserBasicInfo', {
    'id': fields.Integer(description='ID del usuario'),
    'name_user': fields.String(description='Nombre del usuario'),
    'sport': fields.String(description='Deporte'),
    'position': fields.String(description='Posición'),
    'edad': fields.Integer(description='Edad calculada'),
    'city': fields.String(description='Ciudad'),
    'urlphotoperfil': fields.String(description='URL de la foto de perfil'),
    'is_profile_completed': fields.Boolean(description='Perfil completado')
})

# Modelo para error
error_response_model = player_ns.model('ErrorResponse', {
    'error': fields.String(description='Mensaje de error'),
    'codigo': fields.String(description='Código de error')
})