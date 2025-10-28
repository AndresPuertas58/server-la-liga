from app.models.user_model import User
from app.utils.database import db
import re
import bcrypt

class AccountService:
    @staticmethod
    def cambiar_contrasena(user_id: int, data: dict) -> dict:
        """
        Cambiar contraseña del usuario
        """
        try:
            print("=" * 50)
            print("🔄 INICIANDO PROCESO DE CAMBIO DE CONTRASEÑA")
            print("=" * 50)
            print(f"👤 User ID recibido: {user_id}")
            print(f"📦 Datos recibidos: {list(data.keys())}")
            
            # Validar datos requeridos
            required_fields = ['current_password', 'new_password', 'confirm_password']
            print(f"🔍 Validando campos requeridos: {required_fields}")
            
            for field in required_fields:
                if field not in data:
                    print(f"❌ ERROR: Campo faltante: {field}")
                    raise ValueError(f"Campo requerido faltante: {field}")
            
            current_password = data['current_password']
            new_password = data['new_password']
            confirm_password = data['confirm_password']
            
            print("✅ Todos los campos requeridos presentes")
            print(f"📝 Longitud nueva contraseña: {len(new_password)} caracteres")
            
            # Buscar usuario
            print(f"🔍 Buscando usuario en base de datos...")
            user = User.query.get(user_id)
            if not user:
                print("❌ ERROR: Usuario no encontrado en la base de datos")
                raise ValueError("Usuario no encontrado")
            
            print(f"✅ Usuario encontrado: {user.email}")
            print("🔐 Verificando contraseña actual...")
            
            # VERIFICACIÓN ROBUSTA DE CONTRASEÑA ACTUAL
            print(f"🔍 Analizando hash almacenado...")
            print(f"   - Hash actual: '{user.password}'")
            print(f"   - Longitud hash: {len(user.password) if user.password else 0}")
            
            # Si no hay contraseña almacenada, permitir el cambio sin verificación
            if not user.password or user.password.strip() == '':
                print("⚠️  ADVERTENCIA: Usuario sin contraseña hash. Saltando verificación...")
                print("💡 Esto puede pasar si el usuario fue creado sin contraseña o hubo un error previo")
            else:
                # Verificar con bcrypt
                print("🔐 Intentando verificación con bcrypt...")
                try:
                    input_pw = current_password.encode('utf-8')
                    stored_pw = user.password.encode('utf-8')
                    
                    print(f"   - Contraseña a verificar: {current_password[:2]}...")
                    print(f"   - Hash almacenado (inicio): {stored_pw[:20]}...")
                    
                    if not bcrypt.checkpw(input_pw, stored_pw):
                        print("❌ ERROR: Contraseña actual incorrecta")
                        raise ValueError("Contraseña actual incorrecta")
                    
                    print("✅ Contraseña actual verificada correctamente con bcrypt")
                    
                except Exception as bcrypt_error:
                    print(f"❌ Error en bcrypt: {str(bcrypt_error)}")
                    print("🔄 Intentando verificación alternativa...")
                    
                    # Si bcrypt falla, verificar si es un hash de werkzeug
                    if user.password.startswith('pbkdf2:'):
                        print("🔐 Detectado hash werkzeug, pero necesitas usar check_password_hash")
                        raise ValueError("Error en la verificación de contraseña. Contacta al administrador.")
                    else:
                        print("❌ Hash con formato desconocido")
                        raise ValueError("Error en la configuración de la cuenta")
            
            # Validar que las nuevas contraseñas coincidan
            print("🔍 Verificando coincidencia de nuevas contraseñas...")
            if new_password != confirm_password:
                print("❌ ERROR: Las nuevas contraseñas no coinciden")
                raise ValueError("Las nuevas contraseñas no coinciden")
            
            print("✅ Nuevas contraseñas coinciden")
            
            # Validar fortaleza de la nueva contraseña
            print("🔍 Validando fortaleza de nueva contraseña...")
            if len(new_password) < 8:
                print("❌ ERROR: La contraseña es demasiado corta")
                raise ValueError("La contraseña debe tener al menos 8 caracteres")
            
            print("✅ Contraseña cumple con longitud mínima")
            
            # Actualizar contraseña CON BCRYPT
            print("💾 Actualizando contraseña en base de datos con bcrypt...")
            
            # Generar nuevo hash con bcrypt
            new_password_encoded = new_password.encode('utf-8')
            new_hash = bcrypt.hashpw(new_password_encoded, bcrypt.gensalt())
            user.password = new_hash.decode('utf-8')
            
            db.session.commit()
            
            print("✅ Contraseña actualizada exitosamente en la base de datos")
            print(f"🔐 Nuevo hash generado: {user.password[:30]}...")
            print("🎉 PROCESO DE CAMBIO DE CONTRASEÑA COMPLETADO EXITOSAMENTE")
            print("=" * 50)
            
            return {"message": "Contraseña cambiada exitosamente"}
            
        except ValueError as ve:
            print(f"🚨 ERROR DE VALIDACIÓN: {str(ve)}")
            print("=" * 50)
            raise ve
        except Exception as e:
            print(f"💥 ERROR INESPERADO: {str(e)}")
            print("🔄 Realizando rollback de la transacción...")
            db.session.rollback()
            print("✅ Rollback completado")
            print("=" * 50)
            raise Exception(f"Error al cambiar contraseña: {str(e)}")

    @staticmethod
    def cambiar_correo(user_id: int, data: dict) -> dict:
        """
        Cambiar correo electrónico del usuario
        """
        try:
            print("=" * 50)
            print("🔄 INICIANDO PROCESO DE CAMBIO DE CORREO ELECTRÓNICO")
            print("=" * 50)
            print(f"👤 User ID recibido: {user_id}")
            print(f"📦 Datos recibidos: {list(data.keys())}")
            
            # Validar datos requeridos
            required_fields = ['password', 'new_email', 'confirm_email']
            print(f"🔍 Validando campos requeridos: {required_fields}")
            
            for field in required_fields:
                if field not in data:
                    print(f"❌ ERROR: Campo faltante: {field}")
                    raise ValueError(f"Campo requerido faltante: {field}")
            
            password = data['password']
            new_email = data['new_email']
            confirm_email = data['confirm_email']
            
            print("✅ Todos los campos requeridos presentes")
            print(f"📧 Nuevo correo recibido: {new_email}")
            
            # Buscar usuario
            print(f"🔍 Buscando usuario en base de datos...")
            user = User.query.get(user_id)
            if not user:
                print("❌ ERROR: Usuario no encontrado en la base de datos")
                raise ValueError("Usuario no encontrado")
            
            print(f"✅ Usuario encontrado: {user.email} (correo actual)")
            
            # Verificar contraseña
            print("🔐 Verificando contraseña...")
            input_pw = data['password'].encode('utf-8')
            stored_pw = user.password.encode('utf-8')

            # ✅ CORREGIDO: Usar ValueError en lugar de make_response
            if not bcrypt.checkpw(input_pw, stored_pw):
                print("❌ ERROR: Contraseña incorrecta")
                raise ValueError("La contraseña es incorrecta")
            
            print("✅ Contraseña verificada correctamente")
            
            # Validar que los correos coincidan
            print("🔍 Verificando coincidencia de correos...")
            if new_email != confirm_email:
                print("❌ ERROR: Los correos electrónicos no coinciden")
                print(f"   Nuevo correo: {new_email}")
                print(f"   Confirmación: {confirm_email}")
                raise ValueError("Los correos electrónicos no coinciden")
            
            print("✅ Correos electrónicos coinciden")
            
            # Validar formato de correo
            print("🔍 Validando formato de correo electrónico...")
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, new_email):
                print(f"❌ ERROR: Formato de correo inválido: {new_email}")
                raise ValueError("Formato de correo electrónico inválido")
            
            print("✅ Formato de correo válido")
            
            # Verificar si el correo ya existe
            print("🔍 Verificando si el correo ya está en uso...")
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user and existing_user.id != user_id:
                print(f"❌ ERROR: El correo {new_email} ya está registrado por otro usuario")
                raise ValueError("El correo electrónico ya está en uso")
            
            print("✅ Correo disponible para uso")
            
            # Guardar correo anterior para el log
            correo_anterior = user.email
            
            # Actualizar correo
            print("💾 Actualizando correo en base de datos...")
            user.email = new_email
            db.session.commit()
            
            print(f"✅ Correo actualizado exitosamente:")
            print(f"   📧 Anterior: {correo_anterior}")
            print(f"   📧 Nuevo: {new_email}")
            print("🎉 PROCESO DE CAMBIO DE CORREO COMPLETADO EXITOSAMENTE")
            print("=" * 50)
            
            return {"message": "Correo electrónico cambiado exitosamente"}
            
        except ValueError as ve:
            print(f"🚨 ERROR DE VALIDACIÓN: {str(ve)}")
            print("=" * 50)
            raise ve
        except Exception as e:
            print(f"💥 ERROR INESPERADO: {str(e)}")
            print("🔄 Realizando rollback de la transacción...")
            db.session.rollback()
            print("✅ Rollback completado")
            print("=" * 50)
            raise Exception(f"Error al cambiar correo electrónico: {str(e)}")