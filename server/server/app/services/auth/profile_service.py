import os
import uuid
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename
from app.models.user_model import User
from app.utils.database import db
from datetime import datetime

class PlayerService:
    
    @staticmethod
    def create_player_profile(user_id: int, data: dict, profile_picture_file=None) -> dict:
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

            # Validar campos obligatorios
            campos_obligatorios = ['telephone', 'city', 'sport', 'position']
            for campo in campos_obligatorios:
                if campo not in data or not data[campo]:
                    raise ValueError(f"El campo {campo} es obligatorio para completar el perfil")

            # Actualizar campos del perfil
            user.telephone = data['telephone']
            user.city = data['city']
            user.sport = data['sport']
            user.position = data['position']
            
            # Campos opcionales
            if 'biography' in data:
                user.biography = data['biography']

            # ✅ MANEJO DE IMÁGENES DE PERFIL - EXACTAMENTE IGUAL QUE CANCHAS
            if profile_picture_file and profile_picture_file.filename:
                print("🖼️ Procesando imagen de perfil...")
                url_imagen = PlayerService._guardar_y_convertir_a_webp(profile_picture_file, user_id)
                if url_imagen:
                    user.urlphotoperfil = url_imagen
                    print(f"📷 Imagen de perfil guardada: {url_imagen}")
                else:
                    print("❌ No se pudo procesar la imagen de perfil")
            elif 'profilePicture' in data and data['profilePicture']:
                # Manejar URL existente (compatibilidad)
                url = data['profilePicture']
                if isinstance(url, list) and len(url) > 0:
                    user.urlphotoperfil = str(url[0])
                else:
                    user.urlphotoperfil = str(url)
                print(f"📷 URL de imagen de perfil guardada: {user.urlphotoperfil}")
            elif 'urlphotoperfil' in data and data['urlphotoperfil']:
                user.urlphotoperfil = str(data['urlphotoperfil'])
                print(f"📷 URL de imagen de perfil guardada: {data['urlphotoperfil']}")
            else:
                print("⚠️ No se encontró imagen de perfil para guardar.")

            # Marcar perfil como completado
            user.is_profile_completed = True
            user.updated_at = datetime.utcnow()
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
    def _guardar_y_convertir_a_webp(imagen_file, user_id):
        """
        Guardar imagen y convertir a WebP como archivo - EXACTAMENTE IGUAL QUE CANCHAS
        """
        try:
            # Crear directorios específicos para usuarios - Misma estructura que canchas
            upload_folder = os.path.join(current_app.root_path, 'utils', 'pictures', 'users', str(user_id))
            webp_folder = os.path.join(upload_folder, 'webp')
            os.makedirs(webp_folder, exist_ok=True)
            
            # Generar nombres únicos - Mismo formato que canchas
            original_filename = secure_filename(imagen_file.filename)
            name_without_ext = os.path.splitext(original_filename)[0]
            unique_id = uuid.uuid4().hex
            
            # Guardar original temporalmente
            temp_path = os.path.join(upload_folder, f"temp_{unique_id}_{original_filename}")
            imagen_file.save(temp_path)
            
            try:
                # Abrir y procesar imagen - Mismo procesamiento que canchas
                with Image.open(temp_path) as img:
                    # Convertir a RGB si es necesario
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    # Redimensionar (máximo 1200px como canchas, pero para perfil 800px es suficiente)
                    max_size = (800, 800)  # Un poco más pequeño que canchas para optimizar
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Guardar como WebP - Mismo formato que canchas
                    webp_filename = f"{unique_id}_{name_without_ext}.webp"
                    webp_path = os.path.join(webp_folder, webp_filename)
                    
                    # Guardar con calidad optimizada
                    img.save(webp_path, 'WEBP', quality=85, optimize=True)
                    
                    # Retornar ruta relativa del WebP para guardar en BD - Mismo formato que canchas
                    relative_path = f"/utils/pictures/users/{user_id}/webp/{webp_filename}"
                    print(f"🖼️ Imagen convertida a WebP: {original_filename} -> {webp_filename}")
                    
                    return relative_path
                    
            finally:
                # Eliminar archivo temporal - Misma limpieza que canchas
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
        except Exception as e:
            print(f"❌ Error al procesar imagen: {str(e)}")
            return None

    @staticmethod
    def get_profile(user_id: int) -> dict:
        """Obtener perfil completo del jugador con URL accesible de la foto"""
        try:
            print(f"🔍 Buscando perfil del usuario ID: {user_id}")
            
            user = User.query.get(user_id)
            if not user:
                print("❌ Usuario no encontrado")
                raise ValueError("Usuario no encontrado")
            
            if not user.is_profile_completed:
                print("⚠️ Perfil del usuario no está completado")
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
        """Convertir objeto User a diccionario de perfil con URL accesible de foto"""
        
        # Calcular edad
        edad_calculada = None
        if user.fechanacimiento:
            hoy = datetime.now()
            edad_calculada = hoy.year - user.fechanacimiento.year - ((hoy.month, hoy.day) < (user.fechanacimiento.month, user.fechanacimiento.day))
        
        # Construir URL accesible para la foto de perfil si es local - Mismo patrón que canchas
        url_foto_accesible = user.urlphotoperfil
        if user.urlphotoperfil and user.urlphotoperfil.startswith('/utils/pictures/'):
            filename = os.path.basename(user.urlphotoperfil)
            # ✅ URL CORREGIDA: /player/ en lugar de /user/
            url_foto_accesible = f"/player/{user.id}/imagen-perfil/{filename}"
            print(f"🔗 URL de imagen construida: {url_foto_accesible}")
        
        return {
            # Datos del registro
            'id': user.id,
            'email': user.email,
            'name_user': user.name_user,
            'edad': edad_calculada,
            'fechanacimiento': user.fechanacimiento.isoformat() if user.fechanacimiento else None,
            'terms': user.terms,
            'is_profile_completed': user.is_profile_completed,
            'status': user.status,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            
            # Datos del perfil
            'telephone': user.telephone,
            'city': user.city,
            'sport': user.sport,
            'position': user.position,
            'biography': user.biography,
            'urlphotoperfil': url_foto_accesible,  # ✅ URL accesible corregida
            'role': user.role
        }

    @staticmethod
    def actualizar_foto_perfil(user_id: int, profile_picture_file):
        """Actualizar solo la foto de perfil del usuario"""
        try:
            print(f"🖼️ Actualizando foto de perfil para usuario ID: {user_id}")
            
            user = User.query.get(user_id)
            if not user:
                raise ValueError("Usuario no encontrado")
            
            if not profile_picture_file or not profile_picture_file.filename:
                raise ValueError("Archivo de imagen no válido")
            
            # Procesar y guardar la nueva imagen usando el mismo método que canchas
            nueva_url_imagen = PlayerService._guardar_y_convertir_a_webp(profile_picture_file, user_id)
            if not nueva_url_imagen:
                raise ValueError("Error al procesar la imagen")
            
            # Actualizar en la base de datos
            user.urlphotoperfil = nueva_url_imagen
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            print("✅ Foto de perfil actualizada exitosamente")
            
            return {
                'message': 'Foto de perfil actualizada exitosamente',
                'url_imagen': nueva_url_imagen,
                'url_accesible': f"/player/{user_id}/imagen-perfil/{os.path.basename(nueva_url_imagen)}"
            }
            
        except Exception as e:
            print(f"❌ Error al actualizar foto de perfil: {str(e)}")
            db.session.rollback()
            raise e

    @staticmethod
    def eliminar_foto_perfil(user_id: int):
        """Eliminar foto de perfil del usuario"""
        try:
            print(f"🗑️ Eliminando foto de perfil para usuario ID: {user_id}")
            
            user = User.query.get(user_id)
            if not user:
                raise ValueError("Usuario no encontrado")
            
            if not user.urlphotoperfil:
                return {'message': 'El usuario no tiene foto de perfil'}
            
            # Eliminar archivo físico si es local - Misma lógica que canchas
            if user.urlphotoperfil.startswith('/utils/pictures/'):
                ruta_completa = os.path.join(current_app.root_path, user.urlphotoperfil.lstrip('/'))
                if os.path.exists(ruta_completa):
                    os.remove(ruta_completa)
                    print(f"✅ Archivo eliminado: {ruta_completa}")
                
                # También eliminar la carpeta si está vacía
                carpeta_imagen = os.path.dirname(ruta_completa)
                carpeta_padre = os.path.dirname(carpeta_imagen)
                
                if os.path.exists(carpeta_imagen) and not os.listdir(carpeta_imagen):
                    os.rmdir(carpeta_imagen)
                    print(f"✅ Carpeta webp eliminada: {carpeta_imagen}")
                    
                if os.path.exists(carpeta_padre) and not os.listdir(carpeta_padre):
                    os.rmdir(carpeta_padre)
                    print(f"✅ Carpeta usuario eliminada: {carpeta_padre}")
            
            # Actualizar en base de datos
            user.urlphotoperfil = None
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            print("✅ Foto de perfil eliminada exitosamente")
            
            return {'message': 'Foto de perfil eliminada exitosamente'}
            
        except Exception as e:
            print(f"❌ Error al eliminar foto de perfil: {str(e)}")
            db.session.rollback()
            raise e