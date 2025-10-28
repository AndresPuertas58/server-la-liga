import bcrypt
import json
from app.models.user_model import User
from app.utils.database import db
from datetime import datetime
from app.services.email.email_service import EmailService

class AuthService:
    @staticmethod
    def register_user(data):
        try:
            print("🔐 Iniciando proceso de registro...")
            print(f"📧 Email recibido: {data.get('email')}")
            print(f"👤 Nombre recibido: {data.get('name_user')}")
            
            # Verificar campos requeridos
            required_fields = ['name_user', 'email', 'password', 'fechanacimiento']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValueError(f"Campo requerido faltante: {field}")
            
            # Verificar si el email ya existe en la base de datos FINAL
            print("🔍 Verificando si el email ya existe...")
            if User.query.filter_by(email=data['email']).first():
                print("❌ Email ya registrado")
                raise ValueError('El email ya está registrado')
            
            print("✅ Email disponible")

            # Validar y formatear fecha de nacimiento
            print("📅 Procesando fecha de nacimiento...")
            fecha_nacimiento = data['fechanacimiento']
            
            if isinstance(fecha_nacimiento, str):
                try:
                    fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
                    print(f"✅ Fecha de nacimiento parseada: {fecha_nacimiento}")
                except ValueError:
                    raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")
            
            # Calcular edad y validar que sea mayor de 18
            hoy = datetime.now()
            edad_calculada = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            print(f"🎂 Edad calculada: {edad_calculada} años")
            
            if edad_calculada < 18:
                print("❌ Usuario menor de 18 años")
                raise ValueError("Debes ser mayor de 18 años para registrarte")
            
            print("✅ Usuario mayor de 18 años - Validación pasada")

            # Hashear la contraseña
            print("🔐 Hasheando contraseña...")
            hashed_password = bcrypt.hashpw(
                data['password'].encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            print("✅ Contraseña hasheada correctamente")

            # ✅ GENERAR Y ENVIAR CÓDIGO DE VERIFICACIÓN
            print("🔐 Generando código de verificación...")
            verification_code = EmailService.generate_verification_code()
            
            # Enviar email de verificación
            email_sent = EmailService.send_verification_email(
                user_email=data['email'],
                user_name=data['name_user'],
                verification_code=verification_code
            )
            
            if not email_sent:
                raise ValueError("Error al enviar el email de verificación. Intenta nuevamente.")
            
            # Almacenar código de verificación
            EmailService.store_verification_code(data['email'], verification_code)
            
            # ✅ Preparar datos del usuario para almacenamiento temporal
            # ✅ CONVERTIR datetime a string para JSON
            user_data = {
                'name_user': data['name_user'],
                'email': data['email'],
                'hashed_password': hashed_password,
                'fechanacimiento': fecha_nacimiento.isoformat() if isinstance(fecha_nacimiento, datetime) else fecha_nacimiento
            }
            
            print("✅ Proceso de registro inicial completado - Esperando verificación")
            
            return {
                'message': 'Email de verificación enviado. Por favor verifica tu email para completar el registro.',
                'email': data['email'],
                'needs_verification': True,
                'user_data': user_data  # Datos temporales para crear usuario después
            }
            
        except ValueError as ve:
            print(f"❌ Error de validación: {str(ve)}")
            raise ve
        except Exception as e:
            print(f"💥 Error inesperado en registro: {str(e)}")
            raise e

    @staticmethod
    def verify_and_create_user(email, verification_code, user_data):
        """Verificar código y crear usuario final"""
        try:
            print(f"🔐 Verificando código para: {email}")
            
            # Verificar que tenemos los datos del usuario
            if not user_data:
                raise ValueError("Datos de usuario no encontrados")
            
            # Verificar código
            if not EmailService.verify_code(email, verification_code):
                raise ValueError("Código de verificación inválido o expirado")
            
            # Verificar nuevamente que el email no exista (por si acaso)
            if User.query.filter_by(email=email).first():
                raise ValueError("El email ya está registrado")
            
            # ✅ CONVERTIR string de fecha_nacimiento de vuelta a datetime
            if isinstance(user_data['fechanacimiento'], str):
                user_data['fechanacimiento'] = datetime.fromisoformat(user_data['fechanacimiento'])
            
            # Crear usuario final
            print("👤 Creando usuario en base de datos...")
            user = User(
                name_user=user_data['name_user'],
                email=user_data['email'],
                password=user_data['hashed_password'],
                role="player",
                terms=True,
                fechanacimiento=user_data['fechanacimiento']
            )
            
            db.session.add(user)
            db.session.commit()
            
            print("✅ Usuario creado exitosamente después de verificación")
            
            # Limpiar código de verificación
            if email in EmailService.verification_codes:
                del EmailService.verification_codes[email]
            
            # Calcular edad para la respuesta
            hoy = datetime.now()
            edad_calculada = hoy.year - user.fechanacimiento.year - ((hoy.month, hoy.day) < (user.fechanacimiento.month, user.fechanacimiento.day))
            
            return {
                'message': 'Registro completado exitosamente',
                'user': {
                    'id': user.id,
                    'name': user.name_user,
                    'email': user.email,
                    'role': user.role,
                    'fechanacimiento': user.fechanacimiento.isoformat() if user.fechanacimiento else None,
                    'edad': edad_calculada,
                    'is_profile_completed': user.is_profile_completed
                }
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en verificación: {str(e)}")
            raise e

    @staticmethod
    def resend_verification_code(email, name_user):
        """Reenviar código de verificación"""
        try:
            print(f"🔄 Reenviando código de verificación a: {email}")
            
            # Verificar que el email no esté ya registrado
            if User.query.filter_by(email=email).first():
                raise ValueError("El email ya está registrado")
            
            # Generar nuevo código
            new_code = EmailService.generate_verification_code()
            
            # Enviar email
            email_sent = EmailService.send_verification_email(
                user_email=email,
                user_name=name_user,
                verification_code=new_code
            )
            
            if not email_sent:
                raise ValueError("Error al reenviar el email de verificación")
            
            # Actualizar código
            EmailService.store_verification_code(email, new_code)
            
            return {
                'message': 'Nuevo código de verificación enviado',
                'email': email
            }
            
        except Exception as e:
            print(f"❌ Error al reenviar código: {str(e)}")
            raise e