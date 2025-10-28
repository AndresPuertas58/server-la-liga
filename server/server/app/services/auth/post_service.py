from app.models.post_model import Post, PostComentario, PostLike, ComentarioLike
from app.models.user_model import User
from app.utils.database import db
from datetime import datetime

class PostService:
    @staticmethod
    def crear_post(usuario_id: int, data: dict) -> dict:
        """Crear una nueva publicación"""
        try:
            print("📝 Iniciando creación de post...")
            print(f"👤 Usuario autenticado ID: {usuario_id}")
            
            # Validar campos requeridos
            required_fields = ['tipo_post', 'contenido']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValueError(f"Campo requerido faltante: {field}")
            
            # Validar tipo de post
            if data['tipo_post'] not in ['texto', 'foto']:
                raise ValueError("Tipo de post inválido. Debe ser 'texto' o 'foto'")
            
            # Para posts de tipo foto, validar que tenga imagen_url
            if data['tipo_post'] == 'foto' and not data.get('imagen_url'):
                raise ValueError("Los posts de tipo 'foto' deben incluir una imagen_url")
            
            # Crear el post
            post = Post(
                usuario_id=usuario_id,
                tipo_post=data['tipo_post'],
                contenido=data['contenido'],
                imagen_url=data.get('imagen_url')
            )
            
            db.session.add(post)
            db.session.commit()
            
            print("✅ Post creado exitosamente")
            return {
                'message': 'Post creado exitosamente',
                'post': post.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear post: {str(e)}")
            raise e

    @staticmethod
    def obtener_posts(pagina: int = 1, por_pagina: int = 10) -> dict:
        """Obtener lista de posts paginados"""
        try:
            print(f"📄 Obteniendo posts - página {pagina}")
            
            # Query base para posts no eliminados
            query = Post.query.filter_by(eliminado=False)
            
            # Contar total
            total = query.count()
            
            # Obtener posts paginados
            posts = query.order_by(Post.created_at.desc()).paginate(
                page=pagina, per_page=por_pagina, error_out=False
            )
            
            print(f"✅ Encontrados {len(posts.items)} posts")
            return {
                'posts': [post.to_dict() for post in posts.items],
                'paginacion': {
                    'pagina_actual': pagina,
                    'por_pagina': por_pagina,
                    'total_posts': total,
                    'total_paginas': posts.pages
                }
            }
            
        except Exception as e:
            print(f"❌ Error al obtener posts: {str(e)}")
            raise e

    @staticmethod
    def obtener_post_por_id(post_id: int) -> dict:
        """Obtener un post específico por ID"""
        try:
            print(f"🔍 Buscando post ID: {post_id}")
            
            post = Post.query.filter_by(id=post_id, eliminado=False).first()
            if not post:
                raise ValueError("Post no encontrado")
            
            print("✅ Post encontrado")
            return post.to_dict()
            
        except Exception as e:
            print(f"❌ Error al obtener post: {str(e)}")
            raise e

    @staticmethod
    def actualizar_post(post_id: int, usuario_id: int, data: dict) -> dict:
        """Actualizar un post existente"""
        try:
            print(f"✏️ Actualizando post ID: {post_id}")
            print(f"👤 Usuario autenticado ID: {usuario_id}")
            
            post = Post.query.filter_by(id=post_id, eliminado=False).first()
            if not post:
                raise ValueError("Post no encontrado")
            
            # Verificar que el usuario es el dueño del post
            if post.usuario_id != usuario_id:
                raise ValueError("No tienes permisos para editar este post")
            
            # Actualizar campos permitidos
            if 'contenido' in data:
                post.contenido = data['contenido']
            if 'imagen_url' in data:
                post.imagen_url = data['imagen_url']
            
            db.session.commit()
            
            print("✅ Post actualizado exitosamente")
            return {
                'message': 'Post actualizado exitosamente',
                'post': post.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al actualizar post: {str(e)}")
            raise e

    @staticmethod
    def eliminar_post(post_id: int, usuario_id: int) -> dict:
        """Eliminar (soft delete) un post"""
        try:
            print(f"🗑️ Eliminando post ID: {post_id}")
            print(f"👤 Usuario autenticado ID: {usuario_id}")
            
            post = Post.query.filter_by(id=post_id, eliminado=False).first()
            if not post:
                raise ValueError("Post no encontrado")
            
            # Verificar que el usuario es el dueño del post
            if post.usuario_id != usuario_id:
                raise ValueError("No tienes permisos para eliminar este post")
            
            # Soft delete
            post.eliminado = True
            db.session.commit()
            
            print("✅ Post eliminado exitosamente")
            return {'message': 'Post eliminado exitosamente'}
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al eliminar post: {str(e)}")
            raise e

    @staticmethod
    def agregar_comentario(post_id: int, usuario_id: int, data: dict) -> dict:
        """Agregar comentario a un post"""
        try:
            print(f"💬 Agregando comentario al post ID: {post_id}")
            print(f"👤 Usuario autenticado ID: {usuario_id}")
            
            # Validar contenido
            if 'contenido' not in data or not data['contenido']:
                raise ValueError("El contenido del comentario es requerido")
            
            # Verificar que el post existe
            post = Post.query.filter_by(id=post_id, eliminado=False).first()
            if not post:
                raise ValueError("Post no encontrado")
            
            # Crear comentario
            comentario = PostComentario(
                post_id=post_id,
                usuario_id=usuario_id,
                contenido=data['contenido']
            )
            
            db.session.add(comentario)
            db.session.commit()
            
            print("✅ Comentario agregado exitosamente")
            return {
                'message': 'Comentario agregado exitosamente',
                'comentario': comentario.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al agregar comentario: {str(e)}")
            raise e

    @staticmethod
    def obtener_comentarios(post_id: int) -> dict:
        """Obtener comentarios de un post"""
        try:
            print(f"📋 Obteniendo comentarios del post ID: {post_id}")
            
            # Verificar que el post existe
            post = Post.query.filter_by(id=post_id, eliminado=False).first()
            if not post:
                raise ValueError("Post no encontrado")
            
            comentarios = PostComentario.query.filter_by(
                post_id=post_id, eliminado=False
            ).order_by(PostComentario.created_at.asc()).all()
            
            print(f"✅ Encontrados {len(comentarios)} comentarios")
            return {
                'comentarios': [comentario.to_dict() for comentario in comentarios]
            }
            
        except Exception as e:
            print(f"❌ Error al obtener comentarios: {str(e)}")
            raise e

    @staticmethod
    def toggle_like_post(post_id: int, usuario_id: int) -> dict:
        """Agregar o quitar like de un post"""
        try:
            print(f"❤️ Toggle like en post ID: {post_id}")
            print(f"👤 Usuario autenticado ID: {usuario_id}")
            
            # Verificar que el post existe
            post = Post.query.filter_by(id=post_id, eliminado=False).first()
            if not post:
                raise ValueError("Post no encontrado")
            
            # Buscar like existente
            like_existente = PostLike.query.filter_by(
                post_id=post_id, usuario_id=usuario_id
            ).first()
            
            if like_existente:
                # Quitar like
                db.session.delete(like_existente)
                accion = "quitado"
            else:
                # Agregar like
                nuevo_like = PostLike(post_id=post_id, usuario_id=usuario_id)
                db.session.add(nuevo_like)
                accion = "agregado"
            
            db.session.commit()
            
            print(f"✅ Like {accion} exitosamente")
            return {
                'message': f'Like {accion} exitosamente',
                'liked': accion == "agregado"
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al toggle like: {str(e)}")
            raise e

    @staticmethod
    def toggle_like_comentario(comentario_id: int, usuario_id: int) -> dict:
        """Agregar o quitar like de un comentario"""
        try:
            print(f"❤️ Toggle like en comentario ID: {comentario_id}")
            print(f"👤 Usuario autenticado ID: {usuario_id}")
            
            # Verificar que el comentario existe
            comentario = PostComentario.query.filter_by(
                id=comentario_id, eliminado=False
            ).first()
            if not comentario:
                raise ValueError("Comentario no encontrado")
            
            # Buscar like existente
            like_existente = ComentarioLike.query.filter_by(
                comentario_id=comentario_id, usuario_id=usuario_id
            ).first()
            
            if like_existente:
                # Quitar like
                db.session.delete(like_existente)
                accion = "quitado"
            else:
                # Agregar like
                nuevo_like = ComentarioLike(
                    comentario_id=comentario_id, usuario_id=usuario_id
                )
                db.session.add(nuevo_like)
                accion = "agregado"
            
            db.session.commit()
            
            print(f"✅ Like {accion} exitosamente")
            return {
                'message': f'Like {accion} exitosamente',
                'liked': accion == "agregado"
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al toggle like comentario: {str(e)}")
            raise e

    # NUEVOS MÉTODOS PARA OBTENER CONTENIDO POR USUARIO AUTENTICADO
    @staticmethod
    def obtener_mis_posts(usuario_id: int, pagina: int = 1, por_pagina: int = 10) -> dict:
        """Obtener posts del usuario autenticado"""
        try:
            print(f"📄 Obteniendo posts del usuario ID: {usuario_id} - página {pagina}")
            
            # Query para posts del usuario no eliminados
            query = Post.query.filter_by(usuario_id=usuario_id, eliminado=False)
            
            # Contar total
            total = query.count()
            
            # Obtener posts paginados
            posts = query.order_by(Post.created_at.desc()).paginate(
                page=pagina, per_page=por_pagina, error_out=False
            )
            
            print(f"✅ Encontrados {len(posts.items)} posts del usuario")
            return {
                'posts': [post.to_dict() for post in posts.items],
                'paginacion': {
                    'pagina_actual': pagina,
                    'por_pagina': por_pagina,
                    'total_posts': total,
                    'total_paginas': posts.pages
                }
            }
            
        except Exception as e:
            print(f"❌ Error al obtener posts del usuario: {str(e)}")
            raise e

    @staticmethod
    def obtener_mis_likes_posts(usuario_id: int, pagina: int = 1, por_pagina: int = 10) -> dict:
        """Obtener posts que el usuario autenticado ha dado like"""
        try:
            print(f"❤️ Obteniendo posts likeados por usuario ID: {usuario_id}")
            
            # Query para posts likeados por el usuario
            query = Post.query.join(PostLike).filter(
                PostLike.usuario_id == usuario_id,
                Post.eliminado == False
            )
            
            # Contar total
            total = query.count()
            
            # Obtener posts paginados
            posts = query.order_by(PostLike.created_at.desc()).paginate(
                page=pagina, per_page=por_pagina, error_out=False
            )
            
            print(f"✅ Encontrados {len(posts.items)} posts likeados")
            return {
                'posts': [post.to_dict() for post in posts.items],
                'paginacion': {
                    'pagina_actual': pagina,
                    'por_pagina': por_pagina,
                    'total_posts': total,
                    'total_paginas': posts.pages
                }
            }
            
        except Exception as e:
            print(f"❌ Error al obtener posts likeados: {str(e)}")
            raise e