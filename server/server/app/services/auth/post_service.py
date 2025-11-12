import os
import uuid
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename
from app.models.post_model import Post, PostComentario, PostLike, ComentarioLike
from app.models.user_model import User
from app.utils.database import db
from datetime import datetime

class PostService:
    @staticmethod
    def crear_post(usuario_id: int, data: dict, imagen_file=None) -> dict:
        """Crear una nueva publicación con soporte para imágenes"""
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
            
            # ✅ MANEJO DE IMÁGENES - EXACTAMENTE IGUAL QUE CANCHAS Y PROFILE
            imagen_url = None
            if data['tipo_post'] == 'foto':
                if imagen_file and imagen_file.filename:
                    print("🖼️ Procesando imagen del post...")
                    imagen_url = PostService._guardar_y_convertir_a_webp(imagen_file, usuario_id, 'post')
                    if not imagen_url:
                        raise ValueError("Error al procesar la imagen del post")
                    print(f"📷 Imagen del post guardada: {imagen_url}")
                elif data.get('imagen_url'):
                    # URL existente (compatibilidad)
                    imagen_url = data['imagen_url']
                    print(f"📷 URL de imagen del post: {imagen_url}")
                else:
                    raise ValueError("Los posts de tipo 'foto' deben incluir una imagen")
            
            # Crear el post
            post = Post(
                usuario_id=usuario_id,
                tipo_post=data['tipo_post'],
                contenido=data['contenido'],
                imagen_url=imagen_url
            )
            
            db.session.add(post)
            db.session.commit()
            
            print("✅ Post creado exitosamente")
            return {
                'message': 'Post creado exitosamente',
                'post': PostService._post_to_dict(post)
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear post: {str(e)}")
            raise e

    @staticmethod
    def _guardar_y_convertir_a_webp(imagen_file, user_id, tipo='post'):
        """
        Guardar imagen y convertir a WebP como archivo - EXACTAMENTE IGUAL QUE CANCHAS Y PROFILE
        """
        try:
            # Crear directorios específicos para posts - Misma estructura que canchas y profile
            upload_folder = os.path.join(current_app.root_path, 'utils', 'pictures', 'posts', str(user_id))
            webp_folder = os.path.join(upload_folder, 'webp')
            os.makedirs(webp_folder, exist_ok=True)
            
            # Generar nombres únicos - Mismo formato que canchas y profile
            original_filename = secure_filename(imagen_file.filename)
            name_without_ext = os.path.splitext(original_filename)[0]
            unique_id = uuid.uuid4().hex
            
            # Guardar original temporalmente
            temp_path = os.path.join(upload_folder, f"temp_{unique_id}_{original_filename}")
            imagen_file.save(temp_path)
            
            try:
                # Abrir y procesar imagen - Mismo procesamiento que canchas y profile
                with Image.open(temp_path) as img:
                    # Convertir a RGB si es necesario
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    # Redimensionar (máximo 1200px como canchas)
                    max_size = (1200, 1200)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Guardar como WebP - Mismo formato que canchas y profile
                    webp_filename = f"{unique_id}_{name_without_ext}.webp"
                    webp_path = os.path.join(webp_folder, webp_filename)
                    
                    # Guardar con calidad optimizada
                    img.save(webp_path, 'WEBP', quality=80, optimize=True)
                    
                    # Retornar ruta relativa del WebP para guardar en BD - Mismo formato
                    relative_path = f"/utils/pictures/posts/{user_id}/webp/{webp_filename}"
                    print(f"🖼️ Imagen de post convertida a WebP: {original_filename} -> {webp_filename}")
                    
                    return relative_path
                    
            finally:
                # Eliminar archivo temporal - Misma limpieza que canchas y profile
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
        except Exception as e:
            print(f"❌ Error al procesar imagen de post: {str(e)}")
            return None

    
    @staticmethod
    def _post_to_dict(post: Post) -> dict:
        """Convertir objeto Post a diccionario con URLs accesibles"""
        post_dict = {
            'id': post.id,
            'usuario_id': post.usuario_id,
            'tipo_post': post.tipo_post,
            'contenido': post.contenido,
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'updated_at': post.updated_at.isoformat() if post.updated_at else None,
            'eliminado': post.eliminado,
            'total_comentarios': getattr(post, 'total_comentarios', 0),
            'total_likes': getattr(post, 'total_likes', 0)
        }
        
        # ✅ INFORMACIÓN DEL USUARIO CON FOTO DE PERFIL ACCESIBLE (IGUAL QUE EL SERVICIO DE PERFIL)
        if hasattr(post, 'usuario') and post.usuario:
            # Construir URL accesible para la foto de perfil - MISMO PATRÓN QUE EL SERVICIO DE PERFIL
            url_foto_accesible = post.usuario.urlphotoperfil
            if post.usuario.urlphotoperfil and post.usuario.urlphotoperfil.startswith('/utils/pictures/'):
                filename = os.path.basename(post.usuario.urlphotoperfil)
                url_foto_accesible = f"/player/{post.usuario.id}/imagen-perfil/{filename}"
                print(f"🔗 URL de imagen de perfil construida: {url_foto_accesible}")
            
            post_dict['usuario'] = {
                'id': post.usuario.id,
                'name_user': post.usuario.name_user,
                'urlphotoperfil': url_foto_accesible  # ✅ URL ACCESIBLE CORREGIDA
            }
        
        # ✅ ESTRUCTURA DE IMÁGENES DEL POST (MANTENER LA ACTUAL)
        post_dict['imagenes_webp'] = []
        if post.imagen_url and post.imagen_url.startswith('/utils/pictures/'):
            filename = os.path.basename(post.imagen_url)
            imagen_info = {
                'id': post.id,
                'orden': 0,
                'url_webp': f"/posts/{post.usuario_id}/imagen-post/{filename}",
                'nombre': filename,
                'formato': 'webp'
            }
            post_dict['imagenes_webp'].append(imagen_info)
        
        # Mantener compatibilidad
        post_dict['imagen_url_accesible'] = post_dict['imagenes_webp'][0]['url_webp'] if post_dict['imagenes_webp'] else None
        
        return post_dict

    @staticmethod
    def obtener_posts(pagina: int = 1, por_pagina: int = 10) -> dict:
        """Obtener lista de posts paginados con información completa del usuario"""
        try:
            print(f"📄 Obteniendo posts - página {pagina}")
            
            # Query base para posts no eliminados con JOIN para traer información del usuario
            query = db.session.query(Post).join(User).filter(
                Post.eliminado == False,
                User.id == Post.usuario_id
            )
            
            # Contar total
            total = query.count()
            
            # Obtener posts paginados
            posts = query.order_by(Post.created_at.desc()).paginate(
                page=pagina, per_page=por_pagina, error_out=False
            )
            
            # Procesar posts con información completa
            posts_con_totales = []
            for post in posts.items:
                post_dict = PostService._post_to_dict(post)
                
                # Contar comentarios no eliminados
                total_comentarios = PostComentario.query.filter_by(
                    post_id=post.id, eliminado=False
                ).count()
                post_dict['total_comentarios'] = total_comentarios
                
                # Contar likes
                total_likes = PostLike.query.filter_by(post_id=post.id).count()
                post_dict['total_likes'] = total_likes
                
                posts_con_totales.append(post_dict)
            
            print(f"✅ Encontrados {len(posts_con_totales)} posts con información de usuarios")
            return {
                'success': True,
                'data': posts_con_totales,
                'count': len(posts_con_totales),
                'total_posts': total,
                'paginacion': {
                    'pagina_actual': pagina,
                    'por_pagina': por_pagina,
                    'total_posts': total,
                    'total_paginas': posts.pages
                },
                'formato_imagenes': 'webp_url'
            }
            
        except Exception as e:
            print(f"❌ Error al obtener posts: {str(e)}")
            raise e
    @staticmethod
    def obtener_post_por_id(post_id: int) -> dict:
        """Obtener un post específico por ID con URL accesible"""
        try:
            print(f"🔍 Buscando post ID: {post_id}")
            
            post = Post.query.filter_by(id=post_id, eliminado=False).first()
            if not post:
                raise ValueError("Post no encontrado")
            
            print("✅ Post encontrado")
            return PostService._post_to_dict(post)
            
        except Exception as e:
            print(f"❌ Error al obtener post: {str(e)}")
            raise e

    @staticmethod
    def actualizar_post(post_id: int, usuario_id: int, data: dict, imagen_file=None) -> dict:
        """Actualizar un post existente con soporte para nueva imagen"""
        try:
            print(f"✏️ Actualizando post ID: {post_id}")
            print(f"👤 Usuario autenticado ID: {usuario_id}")
            
            post = Post.query.filter_by(id=post_id, eliminado=False).first()
            if not post:
                raise ValueError("Post no encontrado")
            
            # Verificar que el usuario es el dueño del post
            if post.usuario_id != usuario_id:
                raise ValueError("No tienes permisos para editar este post")
            
            # ✅ MANEJO DE NUEVA IMAGEN SI SE PROPORCIONA
            nueva_imagen_url = None
            if imagen_file and imagen_file.filename:
                print("🖼️ Procesando nueva imagen para el post...")
                nueva_imagen_url = PostService._guardar_y_convertir_a_webp(imagen_file, usuario_id, 'post')
                if nueva_imagen_url:
                    # Eliminar imagen anterior si existe y es local
                    if post.imagen_url and post.imagen_url.startswith('/utils/pictures/'):
                        PostService._eliminar_imagen_fisica(post.imagen_url)
                    post.imagen_url = nueva_imagen_url
                    print(f"📷 Nueva imagen del post guardada: {nueva_imagen_url}")
            
            # Actualizar campos permitidos (si no se proporcionó nueva imagen)
            if 'contenido' in data:
                post.contenido = data['contenido']
            if 'imagen_url' in data and not imagen_file:
                # Solo actualizar URL si no se subió nueva imagen
                post.imagen_url = data['imagen_url']
            
            db.session.commit()
            
            print("✅ Post actualizado exitosamente")
            return {
                'message': 'Post actualizado exitosamente',
                'post': PostService._post_to_dict(post)
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al actualizar post: {str(e)}")
            raise e

    @staticmethod
    def _eliminar_imagen_fisica(ruta_imagen):
        """Eliminar archivo físico de imagen - Misma lógica que canchas y profile"""
        try:
            if ruta_imagen.startswith('/utils/pictures/'):
                ruta_completa = os.path.join(current_app.root_path, ruta_imagen.lstrip('/'))
                if os.path.exists(ruta_completa):
                    os.remove(ruta_completa)
                    print(f"✅ Archivo de imagen eliminado: {ruta_completa}")
                    
                    # También eliminar carpetas vacías
                    carpeta_imagen = os.path.dirname(ruta_completa)
                    carpeta_padre = os.path.dirname(carpeta_imagen)
                    
                    if os.path.exists(carpeta_imagen) and not os.listdir(carpeta_imagen):
                        os.rmdir(carpeta_imagen)
                        print(f"✅ Carpeta webp eliminada: {carpeta_imagen}")
                        
                    if os.path.exists(carpeta_padre) and not os.listdir(carpeta_padre):
                        os.rmdir(carpeta_padre)
                        print(f"✅ Carpeta posts eliminada: {carpeta_padre}")
        except Exception as e:
            print(f"⚠️ Error al eliminar archivo físico: {str(e)}")

    @staticmethod
    def eliminar_post(post_id: int, usuario_id: int) -> dict:
        """Eliminar (soft delete) un post y su imagen física"""
        try:
            print(f"🗑️ Eliminando post ID: {post_id}")
            print(f"👤 Usuario autenticado ID: {usuario_id}")
            
            post = Post.query.filter_by(id=post_id, eliminado=False).first()
            if not post:
                raise ValueError("Post no encontrado")
            
            # Verificar que el usuario es el dueño del post
            if post.usuario_id != usuario_id:
                raise ValueError("No tienes permisos para eliminar este post")
            
            # Eliminar imagen física si existe
            if post.imagen_url and post.imagen_url.startswith('/utils/pictures/'):
                PostService._eliminar_imagen_fisica(post.imagen_url)
            
            # Soft delete
            post.eliminado = True
            db.session.commit()
            
            print("✅ Post eliminado exitosamente")
            return {'message': 'Post eliminado exitosamente'}
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al eliminar post: {str(e)}")
            raise e

    # ... (los demás métodos se mantienen igual: agregar_comentario, obtener_comentarios, toggle_like_post, toggle_like_comentario, obtener_mis_posts, obtener_mis_likes_posts)

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

    @staticmethod
    def obtener_mis_posts(usuario_id: int, pagina: int = 1, por_pagina: int = 10) -> dict:
        """Obtener posts del usuario autenticado con estructura mejorada"""
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
            
            # Procesar posts con la nueva estructura
            posts_con_totales = []
            for post in posts.items:
                post_dict = PostService._post_to_dict(post)
                
                total_comentarios = PostComentario.query.filter_by(
                    post_id=post.id, eliminado=False
                ).count()
                post_dict['total_comentarios'] = total_comentarios
                
                total_likes = PostLike.query.filter_by(post_id=post.id).count()
                post_dict['total_likes'] = total_likes
                
                posts_con_totales.append(post_dict)
            
            print(f"✅ Encontrados {len(posts_con_totales)} posts del usuario")
            return {
                'success': True,
                'data': posts_con_totales,
                'count': len(posts_con_totales),
                'total_posts': total,
                'paginacion': {
                    'pagina_actual': pagina,
                    'por_pagina': por_pagina,
                    'total_posts': total,
                    'total_paginas': posts.pages
                },
                'formato_imagenes': 'webp_url'
            }
            
        except Exception as e:
            print(f"❌ Error al obtener posts del usuario: {str(e)}")
            raise e

    @staticmethod
    def obtener_mis_likes_posts(usuario_id: int, pagina: int = 1, por_pagina: int = 10) -> dict:
        """Obtener posts que el usuario autenticado ha dado like con URLs accesibles"""
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
                'posts': [PostService._post_to_dict(post) for post in posts.items],
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