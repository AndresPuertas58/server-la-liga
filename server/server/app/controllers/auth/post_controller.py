from flask_restx import Resource
from flask import request, current_app, send_from_directory
import os
from app.services.auth.post_service import PostService
from app.utils.auth_utils import obtener_usuario_desde_token

# ✅ CORREGIDO: Importar desde el __init__ de auth
from . import posts_ns, post_model, post_update_model, comentario_model

# Endpoints para Posts
@posts_ns.route('/create')
class Posts(Resource):
    def post(self):
        """Crear una nueva publicación con soporte para imágenes"""
        print("🌐 [POSTS] Solicitud recibida para crear post")
        print(f"📋 Content-Type: {request.content_type}")
        
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code

        try:
            # ✅ SOPORTAR multipart/form-data para imágenes
            if request.content_type and 'multipart/form-data' in request.content_type:
                print("📦 Datos recibidos como multipart/form-data")
                
                # Obtener datos del form
                data = {
                    'tipo_post': request.form.get('tipo_post'),
                    'contenido': request.form.get('contenido'),
                    'imagen_url': request.form.get('imagen_url')
                }
                
                print(f"📥 Datos recibidos del form: {data}")
                print(f"📁 Archivos recibidos: {list(request.files.keys())}")
                
                # Obtener archivo de imagen
                imagen_file = None
                if 'imagen' in request.files:
                    imagen_file = request.files['imagen']
                    if imagen_file and imagen_file.filename != '':
                        print(f"📸 Archivo de imagen recibido: {imagen_file.filename}")
                        print(f"📏 Tamaño del archivo: {len(imagen_file.read())} bytes")
                        # Reset file pointer después de leer
                        imagen_file.seek(0)
                    else:
                        print("⚠️ Campo 'imagen' existe pero está vacío")
                        imagen_file = None
                else:
                    print("❌ No se encontró campo 'imagen' en los archivos")
                
                # ✅ Llamar al servicio con el archivo de imagen
                result = PostService.crear_post(usuario.id, data, imagen_file)
                
            else:
                # Formato JSON tradicional (sin imagen)
                print("📦 Datos recibidos como JSON")
                data = request.get_json()
                if not data:
                    return {'message': 'Datos inválidos'}, 400
                
                print(f"📥 Datos recibidos: {data}")
                
                # ✅ No permitir tipo 'foto' sin imagen en JSON
                if data.get('tipo_post') == 'foto':
                    return {
                        'message': 'Los posts de tipo "foto" deben enviarse como multipart/form-data con una imagen'
                    }, 400
                
                result = PostService.crear_post(usuario.id, data)
            
            return result, 201
            
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            print(f"❌ Error interno: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'message': 'Error interno del servidor'}, 500

@posts_ns.route('/obtener_post')
class obtenerpost(Resource):
    def get(self):
        """Obtener lista de publicaciones paginadas"""
        print("🌐 [POSTS] Solicitud recibida para obtener posts")
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)

        try:
            result = PostService.obtener_posts(pagina, por_pagina)
            return result, 200
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500
        
@posts_ns.route('/mis-posts')
class MisPosts(Resource):
    def get(self):
        """Obtener las publicaciones del usuario autenticado"""
        print("🌐 [POSTS] Solicitud recibida para obtener mis posts")
        
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)

        try:
            result = PostService.obtener_mis_posts(usuario.id, pagina, por_pagina)
            return result, 200
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500

@posts_ns.route('/mis-likes')
class MisLikes(Resource):
    def get(self):
        """Obtener publicaciones que el usuario autenticado ha dado like"""
        print("🌐 [POSTS] Solicitud recibida para obtener mis likes")
        
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)

        try:
            result = PostService.obtener_mis_likes_posts(usuario.id, pagina, por_pagina)
            return result, 200
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500

@posts_ns.route('/<int:post_id>')
class PostDetail(Resource):
    def get(self, post_id):
        """Obtener una publicación específica"""
        print(f"🌐 [POSTS] Solicitud recibida para obtener post ID: {post_id}")
        
        try:
            result = PostService.obtener_post_por_id(post_id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 404
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500

    def put(self, post_id):
        """Actualizar una publicación con soporte para nueva imagen"""
        print(f"🌐 [POSTS] Solicitud recibida para actualizar post ID: {post_id}")
        print(f"📋 Content-Type: {request.content_type}")
        
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code

        try:
            # ✅ SOPORTAR multipart/form-data para nueva imagen
            imagen_file = None
            data = {}
            
            if request.content_type and 'multipart/form-data' in request.content_type:
                print("📦 Actualizando con multipart/form-data")
                
                # Obtener datos del form
                data = {
                    'contenido': request.form.get('contenido'),
                    'imagen_url': request.form.get('imagen_url'),
                    'tipo_post': request.form.get('tipo_post')
                }
                
                # Obtener archivo de imagen si existe
                if 'imagen' in request.files:
                    imagen_file = request.files['imagen']
                    if imagen_file and imagen_file.filename != '':
                        print(f"📸 Nueva imagen recibida: {imagen_file.filename}")
                    else:
                        imagen_file = None
                
            else:
                # Formato JSON tradicional (sin nueva imagen)
                data = request.get_json()
                if not data:
                    return {'message': 'Datos inválidos'}, 400
            
            result = PostService.actualizar_post(post_id, usuario.id, data, imagen_file)
            return result, 200
            
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            print(f"❌ Error interno: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'message': 'Error interno del servidor'}, 500

    def delete(self, post_id):
        """Eliminar una publicación"""
        print(f"🌐 [POSTS] Solicitud recibida para eliminar post ID: {post_id}")
        
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code

        try:
            result = PostService.eliminar_post(post_id, usuario.id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500

@posts_ns.route('/<int:post_id>/comentarios')
class PostComentarios(Resource):
    @posts_ns.expect(comentario_model)
    def post(self, post_id):
        """Agregar comentario a una publicación"""
        print(f"🌐 [POSTS] Solicitud recibida para agregar comentario al post ID: {post_id}")
        
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        data = request.get_json()
        if not data:
            return {'message': 'Datos inválidos'}, 400

        try:
            result = PostService.agregar_comentario(post_id, usuario.id, data)
            return result, 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500

    def get(self, post_id):
        """Obtener comentarios de una publicación"""
        print(f"🌐 [POSTS] Solicitud recibida para obtener comentarios del post ID: {post_id}")
        
        try:
            result = PostService.obtener_comentarios(post_id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 404
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500

@posts_ns.route('/<int:post_id>/like')
class PostLike(Resource):
    def post(self, post_id):
        """Agregar o quitar like de una publicación"""
        print(f"🌐 [POSTS] Solicitud recibida para toggle like en post ID: {post_id}")
        
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code

        try:
            result = PostService.toggle_like_post(post_id, usuario.id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500

@posts_ns.route('/comentarios/<int:comentario_id>/like')
class ComentarioLike(Resource):
    def post(self, comentario_id):
        """Agregar o quitar like de un comentario"""
        print(f"🌐 [POSTS] Solicitud recibida para toggle like en comentario ID: {comentario_id}")
        
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code

        try:
            result = PostService.toggle_like_comentario(comentario_id, usuario.id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500

# 🔹 Ruta para SERVIR IMÁGENES DE POSTS
@posts_ns.route('/<int:user_id>/imagen-post/<filename>')
class PostImagenResource(Resource):
    def get(self, user_id, filename):
        """Servir archivo WebP de post"""
        try:
            print(f"📤 Sirviendo imagen de post para usuario {user_id}: {filename}")
            
            # Construir ruta al directorio WebP del usuario para posts
            webp_folder = os.path.join(
                current_app.root_path, 
                'utils', 'pictures', 'posts', 
                str(user_id), 'webp'
            )
            
            # Verificar que el archivo existe
            file_path = os.path.join(webp_folder, filename)
            if not os.path.exists(file_path):
                print(f"❌ Archivo WebP no encontrado: {file_path}")
                return {"error": "Imagen de post no encontrada"}, 404
            
            print(f"✅ Sirviendo archivo WebP: {filename}")
            return send_from_directory(webp_folder, filename)
            
        except Exception as e:
            print(f"❌ Error sirviendo imagen de post: {str(e)}")
            return {"error": "Error al cargar imagen de post"}, 500