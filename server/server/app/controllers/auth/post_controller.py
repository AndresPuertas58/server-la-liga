from flask_restx import Resource
from flask import request
from app.services.auth.post_service import PostService
from app.utils.auth_utils import obtener_usuario_desde_token

# ✅ CORREGIDO: Importar desde el __init__ de auth
from . import posts_ns, post_model, post_update_model, comentario_model

# Endpoints para Posts
@posts_ns.route('/create')
class Posts(Resource):
    @posts_ns.expect(post_model)
    def post(self):
        """Crear una nueva publicación"""
        print("🌐 [POSTS] Solicitud recibida para crear post")
        
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        data = request.get_json()
        if not data:
            return {'message': 'Datos inválidos'}, 400

        try:
            # ✅ El usuario_id se obtiene del token automáticamente
            result = PostService.crear_post(usuario.id, data)
            return result, 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
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
            # ✅ El usuario_id se obtiene del token automáticamente
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
            # ✅ El usuario_id se obtiene del token automáticamente
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

    @posts_ns.expect(post_update_model)
    def put(self, post_id):
        """Actualizar una publicación"""
        print(f"🌐 [POSTS] Solicitud recibida para actualizar post ID: {post_id}")
        
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code
        
        data = request.get_json()
        if not data:
            return {'message': 'Datos inválidos'}, 400

        try:
            # ✅ El usuario_id se obtiene del token automáticamente
            result = PostService.actualizar_post(post_id, usuario.id, data)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500

    def delete(self, post_id):
        """Eliminar una publicación"""
        print(f"🌐 [POSTS] Solicitud recibida para eliminar post ID: {post_id}")
        
        # Obtener usuario desde el token JWT
        usuario, error, status_code = obtener_usuario_desde_token()
        if error:
            return error, status_code

        try:
            # ✅ El usuario_id se obtiene del token automáticamente
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
            # ✅ El usuario_id se obtiene del token automáticamente
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
            # ✅ El usuario_id se obtiene del token automáticamente
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
            # ✅ El usuario_id se obtiene del token automáticamente
            result = PostService.toggle_like_comentario(comentario_id, usuario.id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Error interno del servidor'}, 500