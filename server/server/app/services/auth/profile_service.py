from app.models.user_model import User
from app.utils.database import db
from datetime import datetime

class PlayerService:
    @staticmethod
    def create_player_profile(user_id: int, data: dict) -> dict:
        try:
            print("🔍 Iniciando creación/actualización de perfil de jugador...")
            print(f"📋 User ID recibido: {user_id}")

            # Buscar usuario
            print("👤 Buscando usuario en la base de datos...")
            user = User.query.get(user_id)
            if not user:
                print("❌ ERROR: Usuario no encontrado en la base de datos")
                raise ValueError("Usuario no encontrado")
            
            print(f"✅ Usuario encontrado: {user.email}")
            print(f"📊 Datos actuales del usuario:")
            print(f"   - Nombre: {user.name_user}")
            print(f"   - Fecha nacimiento: {user.fechanacimiento}")
            print(f"   - Términos aceptados: {user.terms}")
            print(f"   - Perfil completado: {user.is_profile_completed}")
            print(f"   - Estado: {user.status}")

            # Actualizar CAMPOS QUE VIENEN DEL FORMULARIO DE PERFIL
            print("📝 Actualizando datos del perfil del jugador...")
            
            # ✅ CORREGIDO: Ya no pedimos age, solo estos campos
            campos_obligatorios = ['telephone', 'city', 'sport', 'position']
            for campo in campos_obligatorios:
                if campo not in data or not data[campo]:
                    raise ValueError(f"El campo {campo} es obligatorio para completar el perfil")

            # Actualizar campos del perfil (estos son los que vienen del formulario)
            user.telephone = data['telephone']
            user.city = data['city']
            user.sport = data['sport']
            user.position = data['position']
            
            # Campos opcionales
            if 'biography' in data:
                user.biography = data['biography']
            
            # Procesar imagen de perfil
            print("🖼️ Procesando imagen de perfil...")

            # Verificar si existe alguna clave relacionada con la imagen
            if 'profilePicture' in data and data['profilePicture']:
                url = data['profilePicture']
                
                # Si viene como lista, tomar el primer elemento
                if isinstance(url, list) and len(url) > 0:
                    user.urlphotoperfil = str(url[0])
                    print(f"📷 URL de imagen de perfil guardada: {url[0]}")
                else:
                    user.urlphotoperfil = str(url)
                    print(f"📷 URL de imagen de perfil guardada: {url}")

            elif 'urlphotoperfil' in data and data['urlphotoperfil']:
                user.urlphotoperfil = str(data['urlphotoperfil'])
                print(f"📷 URL de imagen de perfil guardada: {data['urlphotoperfil']}")
            else:
                print("⚠️ No se encontró imagen de perfil para guardar.")

            # Marcar perfil como completado
            user.is_profile_completed = True
            print("✅ Perfil marcado como completado")

            # Guardar cambios
            print("💾 Guardando cambios en la base de datos...")
            db.session.commit()
            print("✅ Cambios guardados exitosamente")

            # Preparar respuesta
            print("🎉 Perfil de jugador creado/actualizado exitosamente!")
            return {
                'message': 'Perfil completado exitosamente',
                'user': PlayerService._user_to_profile_dict(user)
            }

        except ValueError as ve:
            print(f"❌ ERROR de valor: {str(ve)}")
            db.session.rollback()
            raise ve
        except Exception as e:
            print(f"❌ ERROR inesperado al crear perfil de jugador: {str(e)}")
            db.session.rollback()
            raise e

    @staticmethod
    def get_profile(user_id: int) -> dict:
        """Obtener perfil completo del jugador"""
        try:
            print(f"🔍 Buscando perfil del usuario ID: {user_id}")
            
            user = User.query.get(user_id)
            if not user:
                print("❌ Usuario no encontrado")
                raise ValueError("Usuario no encontrado")
            
            if not user.is_profile_completed:
                print("⚠️ Perfil del usuario no está completado")
                # Devolver datos básicos aunque el perfil no esté completo
                return {
                    'message': 'Perfil no completado',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name_user': user.name_user,
                        'fechanacimiento': user.fechanacimiento.isoformat() if user.fechanacimiento else None,
                        'is_profile_completed': user.is_profile_completed,
                        'has_basic_info': bool(user.name_user)
                    }
                }
            
            print(f"✅ Perfil encontrado para: {user.email}")
            return PlayerService._user_to_profile_dict(user)
            
        except Exception as e:
            print(f"❌ Error al obtener perfil: {str(e)}")
            raise e

    @staticmethod
    def _user_to_profile_dict(user: User) -> dict:
        """Convertir objeto User a diccionario de perfil"""
        
        # ✅ Calcular edad a partir de la fecha de nacimiento
        edad_calculada = None
        if user.fechanacimiento:
            hoy = datetime.now()
            edad_calculada = hoy.year - user.fechanacimiento.year - ((hoy.month, hoy.day) < (user.fechanacimiento.month, user.fechanacimiento.day))
        
        return {
            # Datos del registro (siempre presentes)
            'id': user.id,
            'email': user.email,
            'name_user': user.name_user,
            'edad': edad_calculada,  # ✅ Calculada al momento
            'fechanacimiento': user.fechanacimiento.isoformat() if user.fechanacimiento else None,
            'terms': user.terms,
            'is_profile_completed': user.is_profile_completed,
            'status': user.status,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            
            # Datos del perfil (se completan después)
            'telephone': user.telephone,
            'city': user.city,
            'sport': user.sport,
            'position': user.position,
            'biography': user.biography,
            'urlphotoperfil': user.urlphotoperfil,
            'role': user.role
        }