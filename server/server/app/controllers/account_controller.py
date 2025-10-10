# app/controllers/account_controller.py
from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.account_service import AccountService
from app.utils.auth_utils import obtener_usuario_desde_token

# Namespace para gestión de cuenta
account_ns = Namespace('account', description='Operaciones de gestión de cuenta')

# Modelos para Swagger
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

# Endpoint para cambio de contraseña
@account_ns.route('/cambiar-contrasena')
class CambioContrasena(Resource):
    @account_ns.expect(cambio_contrasena_model)
    def post(self):
        """Cambiar contraseña del usuario logueado"""
        print("🌐 [CONTROLLER] Solicitud recibida para cambio de contraseña")
        
        # Obtener usuario desde el token JWT
        print("🔐 [CONTROLLER] Obteniendo usuario desde token...")
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            print(f"❌ [CONTROLLER] Error de autenticación: {error}")
            return error, status_code
        
        print(f"✅ [CONTROLLER] Usuario autenticado: {usuario.email}")
        
        data = request.get_json()
        if not data:
            print("❌ [CONTROLLER] No se recibieron datos JSON")
            return {'message': 'Datos inválidos'}, 400

        print("📥 [CONTROLLER] Datos JSON recibidos correctamente")

        try:
            print("🚀 [CONTROLLER] Llamando al servicio de cambio de contraseña...")
            result = AccountService.cambiar_contrasena(usuario.id, data)
            print("✅ [CONTROLLER] Servicio completado exitosamente")
            return result, 200
        except ValueError as e:
            print(f"🚨 [CONTROLLER] Error de validación: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            print(f"💥 [CONTROLLER] Error interno: {str(e)}")
            return {'message': 'Error interno del servidor'}, 500

# Endpoint para cambio de correo electrónico
@account_ns.route('/cambiar-correo')
class CambioCorreo(Resource):
    @account_ns.expect(cambio_correo_model)
    def post(self):
        """Cambiar correo electrónico del usuario logueado"""
        print("🌐 [CONTROLLER] Solicitud recibida para cambio de correo")
        
        # Obtener usuario desde el token JWT
        print("🔐 [CONTROLLER] Obteniendo usuario desde token...")
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            print(f"❌ [CONTROLLER] Error de autenticación: {error}")
            return error, status_code
        
        print(f"✅ [CONTROLLER] Usuario autenticado: {usuario.email}")
        
        data = request.get_json()
        if not data:
            print("❌ [CONTROLLER] No se recibieron datos JSON")
            return {'message': 'Datos inválidos'}, 400

        print("📥 [CONTROLLER] Datos JSON recibidos correctamente")

        try:
            print("🚀 [CONTROLLER] Llamando al servicio de cambio de correo...")
            result = AccountService.cambiar_correo(usuario.id, data)
            print("✅ [CONTROLLER] Servicio completado exitosamente")
            return result, 200
        except ValueError as e:
            print(f"🚨 [CONTROLLER] Error de validación: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            print(f"💥 [CONTROLLER] Error interno: {str(e)}")
            return {'message': 'Error interno del servidor'}, 500