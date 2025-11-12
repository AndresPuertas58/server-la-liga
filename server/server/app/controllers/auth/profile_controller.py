from app.models.user_model import User
from app.utils.database import db
from datetime import datetime
from app.utils.auth_utils import obtener_usuario_desde_token
from flask import request, send_from_directory, current_app
from flask_restx import Resource
import os
from app.services.auth.profile_service import PlayerService

# Importar desde el archivo de modelos Swagger
from .swagger_models import (
    player_profile_model, 
    player_profile_response,
    profile_picture_response,
    user_basic_info_model,
    error_response_model,
)
from . import player_ns


# 🔹 Obtener perfil de jugador (por ID o por token si no se pasa ID)
@player_ns.route('/profile', defaults={'user_id': None})
@player_ns.route('/profile/<int:user_id>')
class PlayerProfileById(Resource):
    @player_ns.response(200, 'Perfil obtenido exitosamente', player_profile_response)
    @player_ns.response(404, 'Usuario no encontrado', error_response_model)
    def get(self, user_id):
        """Obtener perfil de jugador (por ID o token JWT)"""
        # Si no se pasa user_id, obtenerlo desde el token
        if user_id is None:
            usuario, error, status_code = obtener_usuario_desde_token()
            if error:
                return error, status_code
            user_id = usuario.id
            print(f"🧩 Obtenido user_id desde token: {user_id}")

        # Llamar al servicio para obtener el perfil
        result = PlayerService.get_profile(user_id)
        return result, 200


@player_ns.route('/profile_update')
class PlayerProfile(Resource):
    @player_ns.expect(player_profile_model)
    @player_ns.response(201, 'Perfil creado/actualizado exitosamente', player_profile_response)
    @player_ns.response(400, 'Datos inválidos', error_response_model)
    @player_ns.response(403, 'No autorizado', error_response_model)
    @player_ns.response(500, 'Error interno del servidor', error_response_model)
    def put(self):
        """Crear o completar el perfil del jugador logueado con soporte para imagen"""
        print("🎯 Llegó request a /profile_user PUT")
        print(f"📋 Content-Type: {request.content_type}")
        print(f"📦 Método: {request.method}")
        print(f"📊 Headers: {dict(request.headers)}")
        
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        if usuario.role != 'player':
            return {'message': 'Solo jugadores pueden completar este perfil'}, 403

        try:
            # ✅ DETECCIÓN MEJORADA DEL TIPO DE CONTENIDO
            content_type = request.content_type or ''
            print(f"🔍 Content-Type detectado: '{content_type}'")
            
            # Verificar si hay datos en form
            has_form_data = any(key in request.form for key in ['telephone', 'city', 'sport', 'position'])
            has_files = 'profilePicture' in request.files
            
            print(f"📝 Tiene datos de formulario: {has_form_data}")
            print(f"📸 Tiene archivos: {has_files}")
            print(f"📋 Keys en request.form: {list(request.form.keys())}")
            print(f"📁 Keys en request.files: {list(request.files.keys())}")
            
            # ✅ SOPORTAR multipart/form-data para imágenes
            if has_form_data or has_files:
                print("📦 Procesando como multipart/form-data")
                
                # Obtener datos del form
                data = {
                    'telephone': request.form.get('telephone'),
                    'city': request.form.get('city'),
                    'sport': request.form.get('sport'),
                    'position': request.form.get('position'),
                    'biography': request.form.get('biography')
                }
                
                print(f"📥 Datos recibidos del form: {data}")
                
                # Obtener archivo de imagen de perfil
                profile_picture_file = None
                if 'profilePicture' in request.files:
                    profile_picture_file = request.files['profilePicture']
                    print(f"📸 Archivo de imagen recibido: {profile_picture_file.filename}")
                    print(f"📏 Tamaño del archivo: {len(profile_picture_file.read())} bytes")
                    # Resetear el stream de lectura
                    profile_picture_file.seek(0)
                else:
                    print("⚠️ No se recibió archivo de imagen")
                
                # Validar campos obligatorios
                campos_obligatorios = ['telephone', 'city', 'sport', 'position']
                campos_faltantes = [campo for campo in campos_obligatorios if not data.get(campo)]
                if campos_faltantes:
                    return {'message': f'Campos obligatorios faltantes: {", ".join(campos_faltantes)}'}, 400
                
                # Llamar al servicio con el archivo de imagen
                result = PlayerService.create_player_profile(
                    usuario.id, 
                    data, 
                    profile_picture_file=profile_picture_file
                )
                
            # ✅ SOPORTAR JSON tradicional
            elif content_type == 'application/json' or request.get_data():
                print("📦 Intentando procesar como JSON")
                
                try:
                    # Forzar la lectura de JSON incluso sin Content-Type
                    if request.get_data():
                        data = request.get_json(force=True, silent=True)
                        if data:
                            print(f"📥 Datos JSON recibidos: {data}")
                            
                            # Validar campos obligatorios
                            campos_obligatorios = ['telephone', 'city', 'sport', 'position']
                            campos_faltantes = [campo for campo in campos_obligatorios if campo not in data or not data[campo]]
                            if campos_faltantes:
                                return {'message': f'Campos obligatorios faltantes: {", ".join(campos_faltantes)}'}, 400
                            
                            result = PlayerService.create_player_profile(usuario.id, data)
                        else:
                            return {'message': 'No se pudieron procesar los datos JSON'}, 400
                    else:
                        return {'message': 'No se recibieron datos'}, 400
                        
                except Exception as json_error:
                    print(f"❌ Error procesando JSON: {str(json_error)}")
                    return {'message': 'Error al procesar datos JSON'}, 400
                
            else:
                print("❌ No se pudo determinar el tipo de contenido")
                return {
                    'message': 'Content-Type no soportado. Use multipart/form-data para imágenes o application/json para datos simples'
                }, 415
            
            return result, 201
            
        except ValueError as e:
            print(f"❌ Error de validación: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            print(f"❌ Error interno: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'message': 'Error interno del servidor'}, 500

    @player_ns.response(200, 'Perfil obtenido exitosamente', player_profile_response)
    @player_ns.response(403, 'No autorizado', error_response_model)
    @player_ns.response(404, 'Perfil no encontrado', error_response_model)
    def get(self):
        """Obtener perfil del jugador logueado"""
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        if usuario.role != 'player':
            return {'message': 'Solo jugadores pueden acceder a este perfil'}, 403

        try:
            result = PlayerService.get_profile(usuario.id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 404


# 🔹 Ruta para ACTUALIZAR SOLO LA FOTO DE PERFIL
@player_ns.route('/profile_user/picture')
class PlayerProfilePicture(Resource):
    @player_ns.response(200, 'Foto de perfil actualizada exitosamente', profile_picture_response)
    @player_ns.response(400, 'Archivo inválido', error_response_model)
    @player_ns.response(403, 'No autorizado', error_response_model)
    @player_ns.response(500, 'Error interno del servidor', error_response_model)
    def put(self):
        """Actualizar solo la foto de perfil del jugador"""
        print("🎯 Llegó request a /profile_user/picture PUT")
        
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        if usuario.role != 'player':
            return {'message': 'Solo jugadores pueden actualizar su foto de perfil'}, 403

        try:
            # Verificar que se envió un archivo
            if 'profilePicture' not in request.files:
                return {'message': 'No se envió archivo de imagen'}, 400
            
            profile_picture_file = request.files['profilePicture']
            if not profile_picture_file or not profile_picture_file.filename:
                return {'message': 'Archivo de imagen no válido'}, 400
            
            print(f"📸 Actualizando foto de perfil: {profile_picture_file.filename}")
            
            # Llamar al servicio para actualizar solo la foto
            result = PlayerService.actualizar_foto_perfil(usuario.id, profile_picture_file)
            return result, 200
            
        except ValueError as e:
            print(f"❌ Error de validación: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            print(f"❌ Error interno: {str(e)}")
            return {'message': 'Error interno del servidor'}, 500

    @player_ns.response(200, 'Foto de perfil eliminada exitosamente')
    @player_ns.response(403, 'No autorizado', error_response_model)
    @player_ns.response(500, 'Error interno del servidor', error_response_model)
    def delete(self):
        """Eliminar foto de perfil del jugador"""
        print("🎯 Llegó request a /profile_user/picture DELETE")
        
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        if usuario.role != 'player':
            return {'message': 'Solo jugadores pueden eliminar su foto de perfil'}, 403

        try:
            result = PlayerService.eliminar_foto_perfil(usuario.id)
            return result, 200
            
        except Exception as e:
            print(f"❌ Error interno: {str(e)}")
            return {'message': 'Error interno del servidor'}, 500

# 🔹 Ruta para SERVIR IMÁGENES DE PERFIL DE USUARIO - VERIFICADA
@player_ns.route('/<int:user_id>/imagen-perfil/<filename>')
class UserImagenPerfilResource(Resource):
    def get(self, user_id, filename):
        """Servir archivo WebP de perfil de usuario"""
        try:
            print(f"📤 Sirviendo imagen de perfil para usuario {user_id}: {filename}")
            
            # Construir ruta al directorio WebP del usuario
            webp_folder = os.path.join(
                current_app.root_path, 
                'utils', 'pictures', 'users', 
                str(user_id), 'webp'
            )
            
            # Verificar que el archivo existe
            file_path = os.path.join(webp_folder, filename)
            print(f"🔍 Buscando archivo en: {file_path}")
            
            if not os.path.exists(file_path):
                print(f"❌ Archivo WebP no encontrado: {file_path}")
                return {"error": "Imagen de perfil no encontrada"}, 404
            
            print(f"✅ Archivo encontrado, sirviendo: {filename}")
            return send_from_directory(webp_folder, filename)
            
        except Exception as e:
            print(f"❌ Error sirviendo imagen de perfil: {str(e)}")
            return {"error": "Error al cargar imagen de perfil"}, 500

# 🔹 Ruta para OBTENER DATOS BÁSICOS DEL USUARIO (pública)
@player_ns.route('/<int:user_id>/basic')
class UserBasicInfo(Resource):
    @player_ns.response(200, 'Información básica obtenida', user_basic_info_model)
    @player_ns.response(404, 'Usuario no encontrado', error_response_model)
    @player_ns.response(500, 'Error interno del servidor', error_response_model)
    def get(self, user_id):
        """Obtener información básica pública de un usuario"""
        try:
            print(f"🔍 Obteniendo información básica del usuario ID: {user_id}")
            
            user = User.query.get(user_id)
            if not user:
                return {"error": "Usuario no encontrado"}, 404
            
            # Calcular edad
            edad_calculada = None
            if user.fechanacimiento:
                hoy = datetime.now()
                edad_calculada = hoy.year - user.fechanacimiento.year - ((hoy.month, hoy.day) < (user.fechanacimiento.month, user.fechanacimiento.day))
            
            # Construir URL accesible para la foto
            url_foto_accesible = user.urlphotoperfil
            if user.urlphotoperfil and user.urlphotoperfil.startswith('/utils/pictures/'):
                filename = os.path.basename(user.urlphotoperfil)
                url_foto_accesible = f"/user/{user.id}/imagen-perfil/{filename}"
            
            return {
                'id': user.id,
                'name_user': user.name_user,
                'sport': user.sport,
                'position': user.position,
                'edad': edad_calculada,
                'city': user.city,
                'urlphotoperfil': url_foto_accesible,
                'is_profile_completed': user.is_profile_completed
            }, 200
            
        except Exception as e:
            print(f"❌ Error obteniendo información básica: {str(e)}")
            return {"error": "Error al obtener información del usuario"}, 500