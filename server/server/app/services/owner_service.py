# app/services/owner_service.py
from app.models.owner_model import Owner
from app.models.user_model import User
from app.utils.database import db
from datetime import datetime

class OwnerService:
    @staticmethod
    def create_owner_profile(user_id: int, data: dict) -> dict:
        try:
            print("🔍 Iniciando creación de perfil de dueño...")
            print(f"📋 User ID recibido: {user_id}")

            # Buscar usuario
            print("👤 Buscando usuario en la base de datos...")
            user = User.query.get(user_id)
            if not user:
                print("❌ ERROR: Usuario no encontrado en la base de datos")
                raise ValueError("Usuario no encontrado")
            else:
                print(f"✅ Usuario encontrado: {user.email}")

            print("🏃 Buscando perfil de dueño existente...")
            owner = Owner.query.filter_by(user_id=user_id).first()
            if not owner:
                print("📝 Creando nuevo perfil de dueño...")
                owner = Owner(user_id=user_id)
            else:
                print("🔄 Actualizando perfil de dueño existente...")

            # Actualizar datos
            print("📝 Actualizando datos del dueño...")
            owner.nombre_administrador = data['nombre_administrador']
            owner.telefono = data['telefono']
            owner.updated_at = datetime.utcnow()

            db.session.add(owner)

            print("✅ Datos del dueño actualizados")
            user.is_profile_completed = True
            print("✅ Perfil marcado como completado")

            print("💾 Guardando cambios en la base de datos...")
            db.session.commit()
            print("✅ Cambios guardados exitosamente")

            print("🎉 Perfil de dueño creado/actualizado exitosamente!")
            return {
                'owner': owner.to_dict(),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'is_profile_completed': user.is_profile_completed,
                }
            }

        except ValueError as ve:
            print(f"❌ ERROR de valor: {str(ve)}")
            raise ve
        except KeyError as ke:
            print(f"❌ ERROR de clave faltante: {str(ke)}")
            raise ValueError(f'Campo faltante: {str(ke)}')
        except Exception as e:
            print(f"❌ ERROR inesperado al crear perfil de dueño: {str(e)}")
            raise e
        
    @staticmethod
    def get_owner_profile(user_id: int) -> dict:
        try:
            print(f"🔍 Buscando perfil de dueño para user_id: {user_id}")
            
            owner = Owner.query.filter_by(user_id=user_id).first()
            if not owner:
                print("❌ Perfil de dueño no encontrado")
                raise ValueError("Perfil de dueño no encontrado")

            user = User.query.get(user_id)
            if not user:
                print("❌ Usuario no encontrado")
                raise ValueError("Usuario no encontrado")

            print("✅ Perfil de dueño encontrado")
            return {
                'owner': owner.to_dict(),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'is_profile_completed': user.is_profile_completed
                }
            }
            
        except Exception as e:
            print(f"❌ Error al obtener perfil de dueño: {str(e)}")
            raise e