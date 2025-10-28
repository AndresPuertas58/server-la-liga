"""
Módulo de autenticación
Gestiona registro, login, logout y verificación de sesiones
"""
from flask_restx import fields, Namespace

# 📦 Crear namespaces
auth_ns = Namespace('auth', description='Operaciones de autenticación')
player_ns = Namespace('player', description='Operaciones del jugador')
account_ns = Namespace('account', description='Operaciones de gestión de cuenta')
posts_ns = Namespace('posts', description='Operaciones de publicaciones')
cancha_ns = Namespace('cancha', description='Operaciones con canchas')
reserva_ns = Namespace('reserva', description='Operaciones de reserva') 
                    

# 🎯 Modelos para Swagger
register_model = auth_ns.model('Register', {
    'name_user': fields.String(required=True, example='Juan Pérez'),
    'email': fields.String(required=True, example='user@example.com'),
    'password': fields.String(required=True, example='securepassword123'),
    'fechanacimiento': fields.String(required=True, example='1990-05-15')
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, example='user@example.com'),
    'password': fields.String(required=True, example='securepassword123')
})

# 🎯 Modelos para verificación de sesión
token_data_model = auth_ns.model('TokenData', {
    'user_id': fields.String(description='ID del usuario'),
    'email': fields.String(description='Email del usuario'),
    'exp': fields.Integer(description='Timestamp de expiración'),
    'iat': fields.Integer(description='Timestamp de creación')
})

check_session_success_model = auth_ns.model('CheckSessionSuccess', {
    'authenticated': fields.Boolean(description='Indica si la sesión es válida', example=True),
    'message': fields.String(description='Mensaje descriptivo', example='Sesión válida'),
    'token_data': fields.Nested(token_data_model, description='Datos del token decodificado')
})

check_session_error_model = auth_ns.model('CheckSessionError', {
    'authenticated': fields.Boolean(description='Indica si la sesión es válida', example=False),
    'message': fields.String(description='Mensaje de error', example='Token expirado')
})

check_session_unauthorized_model = auth_ns.model('CheckSessionUnauthorized', {
    'authenticated': fields.Boolean(description='Indica si la sesión es válida', example=False),
    'message': fields.String(description='Mensaje de error', example='No autenticado')
})

server_error_model = auth_ns.model('ServerError', {
    'error': fields.String(description='Mensaje de error del servidor', example='Error al verificar sesión')
})

# Modelo para el perfil del jugador
player_profile_model = player_ns.model('PlayerProfile', {
    'telephone': fields.String(required=True, example='+1234567890'),
    'city': fields.String(required=True, example='Ciudad de México'),
    'sport': fields.String(required=True, example='Fútbol'),
    'position': fields.String(required=True, example='Delantero'),
    'biography': fields.String(required=False, example='Soy un jugador apasionado...'),
    'profilePicture': fields.String(required=False, example='https://example.com/photo.jpg')
})

# MODELO configuracion (cambio contraseña y email)
cambio_contrasena_model = account_ns.model('CambioContrasena', {
    'current_password': fields.String(required=True, description='Contraseña actual'),
    'new_password': fields.String(required=True, description='Nueva contraseña'),
    'confirm_password': fields.String(required=True, description='Confirmación de nueva contraseña')
})

cambio_correo_model = account_ns.model('CambioCorreo', {
    'password': fields.String(required=True, description='Contraseña actual para verificación'),
    'new_email': fields.String(required=True, description='Nuevo correo electrónico'),
    'confirm_email': fields.String(required=True, description='Confirmación del nuevo correo')
})

# Modelos para verificación de email
verify_email_model = auth_ns.model('VerifyEmail', {
    'email': fields.String(required=True, example='user@example.com'),
    'verification_code': fields.String(required=True, example='123456')
})

resend_code_model = auth_ns.model('ResendCode', {
    'email': fields.String(required=True, example='user@example.com'),
    'name_user': fields.String(required=True, example='Juan Pérez')
})

# 🎯 Modelos para Swagger - Posts
post_model = posts_ns.model('Post', {
    'tipo_post': fields.String(required=True, enum=['texto', 'foto'], description='Tipo de post'),
    'contenido': fields.String(required=True, description='Contenido del post'),
    'imagen_url': fields.String(description='URL de la imagen (solo para tipo foto)')
})

post_update_model = posts_ns.model('PostUpdate', {
    'contenido': fields.String(description='Contenido del post'),
    'imagen_url': fields.String(description='URL de la imagen')
})

comentario_model = posts_ns.model('Comentario', {
    'contenido': fields.String(required=True, description='Contenido del comentario')
})

pagination_model = posts_ns.model('Pagination', {
    'pagina_actual': fields.Integer,
    'por_pagina': fields.Integer,
    'total_posts': fields.Integer,
    'total_paginas': fields.Integer
})

post_response_model = posts_ns.model('PostResponse', {
    'id': fields.Integer,
    'usuario_id': fields.Integer,
    'tipo_post': fields.String,
    'contenido': fields.String,
    'imagen_url': fields.String,
    'created_at': fields.String,
    'updated_at': fields.String,
    'usuario': fields.Nested(posts_ns.model('UsuarioPost', {
        'id': fields.Integer,
        'name_user': fields.String,
        'urlphotoperfil': fields.String
    })),
    'total_comentarios': fields.Integer,
    'total_likes': fields.Integer
})

comentario_response_model = posts_ns.model('ComentarioResponse', {
    'id': fields.Integer,
    'post_id': fields.Integer,
    'usuario_id': fields.Integer,
    'contenido': fields.String,
    'created_at': fields.String,
    'usuario': fields.Nested(posts_ns.model('UsuarioComentario', {
        'id': fields.Integer,
        'name_user': fields.String,
        'urlphotoperfil': fields.String
    })),
    'total_likes': fields.Integer
})

# 🎯 Modelos para Swagger - Canchas (ACTUALIZADOS)
horario_model = cancha_ns.model('Horario', {
    'dia_semana': fields.String(required=True, enum=['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']),
    'hora_inicio': fields.String(required=True, example='08:00', description='Hora de inicio en formato HH:MM'),
    'hora_fin': fields.String(required=True, example='22:00', description='Hora de fin en formato HH:MM'),
    'intervalo_minutos': fields.Integer(required=False, example=60, default=60, description='Intervalo entre horarios en minutos'),
    'disponible': fields.Boolean(required=False, example=True, default=True, description='Si el horario está disponible')
})

regla_model = cancha_ns.model('Regla', {
    'regla': fields.String(required=True, example='No se permite fumar')
})

amenidad_model = cancha_ns.model('Amenidad', {
    'amenidad': fields.String(required=True, example='Vestidores')
})

# Modelo principal de cancha (ACTUALIZADO)
cancha_model = cancha_ns.model('Cancha', {
    'nombre': fields.String(required=True, example='Cancha Central'),
    'tipo': fields.String(required=True, example='Fútbol'),
    'subtipo': fields.String(required=True, example='Fútbol 11'),
    'direccion': fields.String(required=True, example='Calle Principal 123'),
    'latitud': fields.Float(required=True, example=19.432608),
    'longitud': fields.Float(required=True, example=-99.133209),
    'direccion_completa': fields.String(required=True, example='Calle Principal 123, Colonia Centro, CDMX'),
    'superficie': fields.String(required=True, example='Sintética'),
    'capacidad': fields.Integer(required=True, example=22),
    'precio_hora': fields.Float(required=True, example=500.0),
    'descripcion': fields.String(required=True, example='Cancha profesional con medidas oficiales'),
    'estado': fields.String(required=False, enum=['activa', 'inactiva', 'en_mantenimiento'], default='activa'),
    'imagenes': fields.List(fields.String, required=False, example=['https://example.com/imagen1.jpg']),
    'horarios': fields.List(fields.Nested(horario_model), required=False, description='Lista de rangos horarios por día'),
    'reglas': fields.List(fields.Nested(regla_model), required=False),
    'amenidades': fields.List(fields.Nested(amenidad_model), required=False)
})

# Modelo de respuesta de horario (NUEVO)
horario_response_model = cancha_ns.model('HorarioResponse', {
    'id': fields.Integer,
    'dia_semana': fields.String,
    'hora_inicio': fields.String,
    'hora_fin': fields.String,
    'intervalo_minutos': fields.Integer,
    'disponible': fields.Boolean,
    'fecha_creacion': fields.String
})

# Modelo de respuesta de cancha (ACTUALIZADO)
cancha_response_model = cancha_ns.model('CanchaResponse', {
    'id': fields.Integer,
    'nombre': fields.String,
    'tipo': fields.String,
    'subtipo': fields.String,
    'direccion': fields.String,
    'latitud': fields.Float,
    'longitud': fields.Float,
    'direccion_completa': fields.String,
    'superficie': fields.String,
    'capacidad': fields.Integer,
    'precio_hora': fields.Float,
    'descripcion': fields.String,
    'estado': fields.String,
    'owner_id': fields.Integer,
    'imagenes': fields.List(fields.String),
    'horarios': fields.List(fields.Nested(horario_response_model)),
    'reglas': fields.List(fields.Nested(regla_model)),
    'amenidades': fields.List(fields.Nested(amenidad_model))
})

# Modelo para horarios disponibles
horarios_disponibles_model = cancha_ns.model('HorariosDisponibles', {
    'horarios_disponibles': fields.List(fields.String, description='Lista de horarios disponibles en formato HH:MM'),
    'fecha': fields.String(description='Fecha consultada en formato YYYY-MM-DD'),
    'cancha_id': fields.Integer(description='ID de la cancha consultada'),
    'total_disponibles': fields.Integer(description='Número total de horarios disponibles')
})

# Modelo para creación exitosa de cancha (NUEVO)
cancha_creada_response_model = cancha_ns.model('CanchaCreadaResponse', {
    'message': fields.String(example='Cancha creada exitosamente'),
    'cancha': fields.Nested(cancha_response_model)
})

# Modelo para error de validación (NUEVO)
cancha_error_model = cancha_ns.model('CanchaError', {
    'error': fields.String(example='Error en la validación de datos')
})
# 🎯 Modelos para Swagger - Reservas (ACTUALIZADOS)
reserva_model = reserva_ns.model('Reserva', {
    'cancha_id': fields.Integer(required=True, example=1),
    'fecha': fields.String(required=True, description='Formato YYYY-MM-DD', example='2024-12-25'),
    'hora': fields.String(required=True, description='Formato HH:MM (24h)', example='14:00')
})

reserva_response_model = reserva_ns.model('ReservaResponse', {
    'id': fields.Integer,
    'cancha_id': fields.Integer,
    'user_id': fields.Integer,
    'fecha': fields.String,
    'hora': fields.String,
    'estado': fields.String,
    'created_at': fields.String,
    'cancha': fields.Nested(reserva_ns.model('CanchaReserva', {
        'id': fields.Integer,
        'nombre': fields.String,
        'tipo': fields.String,
        'precio_hora': fields.Float
    }))
})

reserva_creada_response_model = reserva_ns.model('ReservaCreadaResponse', {
    'message': fields.String(description='Mensaje de confirmación', example='Reserva realizada correctamente'),
    'reserva': fields.Nested(reserva_response_model)
})

horarios_ocupados_response = reserva_ns.model('HorariosOcupados', {
    'horarios_ocupados': fields.List(fields.String, description='Lista de horarios ocupados en formato HH:MM'),
    'fecha': fields.String(description='Fecha consultada'),
    'cancha_id': fields.Integer(description='ID de la cancha consultada'),
    'total_ocupados': fields.Integer(description='Número total de horarios ocupados')
})

reserva_verificada_model = reserva_ns.model('ReservaVerificada', {
    'reservado': fields.Boolean(description='Indica si el usuario tiene reserva para la fecha'),
    'fecha': fields.String(description='Fecha verificada'),
    'usuario_id': fields.Integer(description='ID del usuario verificado')
})

tiene_reserva_model = reserva_ns.model('TieneReserva', {
    'tiene_reserva': fields.Boolean(description='Indica si el usuario tiene reserva para la cancha y fecha'),
    'cancha_id': fields.Integer(description='ID de la cancha verificada'),
    'fecha': fields.String(description='Fecha verificada')
})

horarios_ocupados_detallados_model = reserva_ns.model('HorariosOcupadosDetallados', {
    'horarios_ocupados': fields.List(fields.String),
    'detalles': fields.List(fields.Nested(reserva_ns.model('DetalleReserva', {
        'hora': fields.String,
        'estado': fields.String,
        'usuario': fields.Nested(reserva_ns.model('UsuarioReserva', {
            'id': fields.Integer,
            'nombre': fields.String,
            'email': fields.String
        })),
        'reserva_id': fields.Integer,
        'created_at': fields.String
    }))),
    'total_reservas': fields.Integer,
    'cancha': fields.Nested(reserva_ns.model('CanchaInfo', {
        'id': fields.Integer,
        'nombre': fields.String,
        'tipo': fields.String,
        'precio_hora': fields.Float
    })),
    'fecha': fields.String
})

# Modelo para respuesta detallada de verificación de reserva
reserva_verificada_detallada_model = reserva_ns.model('ReservaVerificadaDetallada', {
    'tiene_reserva': fields.Boolean(description='Indica si el usuario tiene reserva'),
    'reserva': fields.Nested(reserva_ns.model('ReservaInfo', {
        'id': fields.Integer,
        'hora': fields.String,
        'estado': fields.String,
        'created_at': fields.String,
        'fecha': fields.String
    }), required=False),
    'cancha': fields.Nested(reserva_ns.model('CanchaInfoVerificada', {
        'id': fields.Integer,
        'nombre': fields.String,
        'tipo': fields.String,
        'precio_hora': fields.Float
    }), required=False),
    'fecha': fields.String(required=False),
    'usuario_id': fields.Integer(description='ID del usuario verificado')
})

# Modelo para lista de reservas del usuario
reserva_usuario_model = reserva_ns.model('ReservaUsuario', {
    'id': fields.Integer,
    'cancha_id': fields.Integer,
    'fecha': fields.String,
    'hora': fields.String,
    'estado': fields.String(description='confirmada, cancelada, finalizada'),
    'created_at': fields.String,
    'cancha': fields.Nested(reserva_ns.model('CanchaReservaUsuario', {
        'id': fields.Integer,
        'nombre': fields.String,
        'tipo': fields.String,
        'precio_hora': fields.Float,
        'direccion': fields.String,
        'superficie': fields.String
    }), required=False)
})

lista_reservas_usuario_model = reserva_ns.model('ListaReservasUsuario', {
    'reservas': fields.List(fields.Nested(reserva_usuario_model)),
    'total': fields.Integer,
    'usuario_id': fields.Integer,
    'fecha_consulta': fields.String(description='Fecha y hora de la consulta')
})

# Modelo para reserva de usuario con información completa de cancha
reserva_usuario_completa_model = reserva_ns.model('ReservaUsuarioCompleta', {
    'id': fields.Integer,
    'cancha_id': fields.Integer,
    'fecha': fields.String,
    'hora': fields.String,
    'estado': fields.String,
    'created_at': fields.String,
    'cancha': fields.Nested(reserva_ns.model('CanchaReservaCompleta', {
        'id': fields.Integer,
        'nombre': fields.String,
        'tipo': fields.String,
        'subtipo': fields.String,
        'direccion': fields.String,
        'direccion_completa': fields.String,
        'superficie': fields.String,
        'capacidad': fields.Integer,
        'precio_hora': fields.Float,
        'descripcion': fields.String,
        'estado': fields.String,
        'imagenes': fields.List(fields.String),
        'latitud': fields.Float,
        'longitud': fields.Float
    }))
})

# 🎯 MODELOS PARA CANCELACIÓN DE RESERVAS (ACTUALIZADOS)
reserva_cancelada_response_model = reserva_ns.model('ReservaCanceladaResponse', {
    'message': fields.String(description='Mensaje de confirmación', example='Reserva cancelada exitosamente'),
    'reserva': fields.Nested(reserva_ns.model('ReservaCancelada', {
        'id': fields.Integer,
        'cancha_id': fields.Integer,
        'fecha': fields.String,
        'hora': fields.String,
        'estado': fields.String,
        'cancelada_at': fields.String,
        'motivo': fields.String(description='Razón de la cancelación', example='Cancelación por usuario'),
        'cancha': fields.Nested(reserva_ns.model('CanchaCancelada', {
            'id': fields.Integer,
            'nombre': fields.String,
            'tipo': fields.String,
            'precio_hora': fields.Float
        }), required=False)
    }))
})

# Modelo para error de validación en reservas
reserva_error_model = reserva_ns.model('ReservaError', {
    'error': fields.String(description='Mensaje de error detallado'),
    'codigo': fields.String(description='Código de error', example='HORARIO_NO_DISPONIBLE'),
    'detalles': fields.Raw(description='Información adicional del error')
})

error_response_model = reserva_ns.model('ErrorResponse', {
    'error': fields.String(description='Mensaje de error', example='Error al procesar la solicitud')
})

# Modelo para respuesta de disponibilidad de horario
disponibilidad_horario_model = reserva_ns.model('DisponibilidadHorario', {
    'disponible': fields.Boolean(description='Indica si el horario está disponible'),
    'hora': fields.String(description='Horario verificado'),
    'fecha': fields.String(description='Fecha verificada'),
    'cancha_id': fields.Integer(description='ID de la cancha'),
    'mensaje': fields.String(description='Mensaje descriptivo', example='Horario disponible')
})

# Modelo para conflicto de reserva
conflicto_reserva_model = reserva_ns.model('ConflictoReserva', {
    'conflicto': fields.Boolean(description='Indica si hay conflicto'),
    'reserva_existente': fields.Nested(reserva_usuario_model, required=False),
    'mensaje': fields.String(description='Descripción del conflicto')
})

# 📥 Importar controladores (esto registra las rutas automáticamente)
from app.controllers.auth.register_controller import Register
from app.controllers.auth.login_controller import Login 
from app.controllers.auth.logout_controller import Logout
from app.controllers.auth.profile_controller import PlayerProfile
from app.controllers.auth.post_controller import Posts, PostDetail, PostComentarios, PostLike, ComentarioLike, MisPosts, MisLikes, obtenerpost
from app.controllers.auth.account_controller import CambioContrasena, CambioCorreo
from app.controllers.auth.cancha_controller import CanchaCreateResource, CanchaListResource, CanchaDetailResource, HorariosDisponiblesResource
from app.controllers.auth.reserva_controller import CrearReservaController, HorariosOcupadosController, VerificarReservaUsuario, MisReservasController, CancelarReservaController  # ✅ Agregado CancelarReservaController
from app.controllers.auth.check_controller import CheckSession

# 📤 Exportar lo necesario
__all__ = [
    'auth_ns',
    'player_ns',
    'account_ns',
    'posts_ns',
    'cancha_ns',
    'reserva_ns',
    'register_model',
    'login_model',
    'token_data_model',
    'check_session_success_model',
    'check_session_error_model',
    'check_session_unauthorized_model',
    'server_error_model',
    'player_profile_model',
    'cambio_contrasena_model',
    'cambio_correo_model',
    'verify_email_model',
    'resend_code_model',
    'post_model',
    'post_update_model',
    'comentario_model',
    'pagination_model',
    'post_response_model',
    'comentario_response_model',
    'horario_model',
    'regla_model',
    'amenidad_model',
    'cancha_model',
    'cancha_response_model',
    'horarios_disponibles_model',
    'reserva_model',
    'reserva_response_model',
    'horarios_ocupados_response',
    'reserva_verificada_model',
    'tiene_reserva_model',
    'reserva_cancelada_response_model',  # ✅ Nuevo modelo
    'error_response_model',  # ✅ Nuevo modelo
    'Register',
    'Login',
    'Logout',
    'PlayerProfile',
    'Posts',
    'PostDetail',
    'PostComentarios', 
    'PostLike',
    'ComentarioLike',
    'MisPosts',
    'MisLikes',
    'obtenerpost',
    'CambioContrasena',
    'CambioCorreo',
    'CanchaCreateResource',
    'CanchaListResource',
    'CanchaDetailResource',
    'HorariosDisponiblesResource',
    'CrearReservaController',
    'HorariosOcupadosController',
    'VerificarReservaUsuario',
    'MisReservasController',
    'CancelarReservaController',  # ✅ Nuevo controlador
    'CheckSession'
]