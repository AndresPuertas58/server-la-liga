"""
Controlador de registro de usuarios
"""

from flask_restx import Resource
from flask import request
from . import auth_ns, register_model, verify_email_model, resend_code_model
from app.services.auth.register_service import AuthService
from app.utils.validation_utils import validate_registration

# Almacenamiento temporal para datos de usuario pendientes de verificación
# En producción, usa Redis o una base de datos temporal
pending_registrations = {}

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'Email de verificación enviado')
    @auth_ns.response(400, 'Error de validación')
    @auth_ns.response(500, 'Error en el servidor')
    def post(self):
        """Registrar nuevo usuario - Paso 1: Enviar código de verificación"""
        print("🌐 [AUTH] Solicitud recibida para registro")
        
        data = auth_ns.payload

        # Validar entrada
        errors = validate_registration(data)
        if errors:
            return {'errors': errors}, 400

        try:
            result = AuthService.register_user(data)
            
            # ✅ Almacenar datos temporales del usuario para usar en la verificación
            if result.get('needs_verification') and 'user_data' in result:
                pending_registrations[data['email']] = result['user_data']
                print(f"💾 Datos temporales almacenados para: {data['email']}")
            
            return result, 201
            
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            print("💥 Error inesperado en el servidor:", str(e))
            return {'error': 'Error en el servidor'}, 500

@auth_ns.route('/verify-email')
class VerifyEmail(Resource):
    @auth_ns.expect(verify_email_model)
    @auth_ns.response(200, 'Usuario verificado y creado exitosamente')
    @auth_ns.response(400, 'Código inválido o expirado')
    @auth_ns.response(404, 'Registro no encontrado')
    @auth_ns.response(500, 'Error en el servidor')
    def post(self):
        """Verificar código de email y completar registro - Paso 2: Crear usuario"""
        print("🌐 [AUTH] Solicitud recibida para verificar email")
        
        data = request.get_json()
        if not data:
            return {'message': 'Datos inválidos'}, 400

        try:
            email = data['email']
            verification_code = data['verification_code']
            
            # ✅ Recuperar datos temporales del usuario
            if email not in pending_registrations:
                return {'message': 'No se encontró un registro pendiente para este email. Por favor, regístrate nuevamente.'}, 404
            
            user_data = pending_registrations[email]
            print(f"🔍 Datos temporales recuperados para: {email}")
            
            # Verificar código y crear usuario
            result = AuthService.verify_and_create_user(
                email=email,
                verification_code=verification_code,
                user_data=user_data
            )
            
            # ✅ Limpiar datos temporales después de verificación exitosa
            if email in pending_registrations:
                del pending_registrations[email]
                print(f"🧹 Datos temporales eliminados para: {email}")
            
            return result, 200
            
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            print(f"💥 Error en verificación de email: {str(e)}")
            return {'message': 'Error interno del servidor'}, 500

@auth_ns.route('/resend-verification')
class ResendVerification(Resource):
    @auth_ns.expect(resend_code_model)
    @auth_ns.response(200, 'Código reenviado exitosamente')
    @auth_ns.response(400, 'Error al reenviar código')
    @auth_ns.response(500, 'Error en el servidor')
    def post(self):
        """Reenviar código de verificación"""
        print("🌐 [AUTH] Solicitud recibida para reenviar código")
        
        data = request.get_json()
        if not data:
            return {'message': 'Datos inválidos'}, 400

        try:
            result = AuthService.resend_verification_code(
                email=data['email'],
                name_user=data['name_user']
            )
            return result, 200
            
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            print(f"💥 Error al reenviar código: {str(e)}")
            return {'message': 'Error interno del servidor'}, 500