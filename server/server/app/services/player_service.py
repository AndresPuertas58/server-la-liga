# app/services/player_service.py
from app.models.player_model import Player
from app.models.user_model import User
from app.models.imagen import Imagen
from app.utils.database import db
from datetime import datetime

class PlayerService:
    @staticmethod
    def create_player_profile(user_id: int, data: dict) -> dict:
        try:
            print("🔍 Iniciando creación de perfil de jugador...")
            print(f"📋 User ID recibido: {user_id}")

            # Buscar usuario
            print("👤 Buscando usuario en la base de datos...")
            user = User.query.get(user_id)
            if not user:
                print("❌ ERROR: Usuario no encontrado en la base de datos")
                raise ValueError("Usuario no encontrado")
            else:
                print(f"✅ Usuario encontrado: {user.email}")

            print("🏃 Buscando perfil de jugador existente...")
            player = Player.query.filter_by(user_id=user_id).first()
            if not player:
                print("📝 Creando nuevo perfil de jugador...")
                player = Player(user_id=user_id)
            else:
                print("🔄 Actualizando perfil de jugador existente...")

            # Actualizar datos
            print("📝 Actualizando datos del jugador...")
            player.deporte = data['deporte']
            player.nombre_completo = data['nombre_completo']
            player.fecha_nacimiento = datetime.fromisoformat(data['fecha_nacimiento']) if data.get('fecha_nacimiento') else None
            player.posicion = data['posicion']
            player.genero = data['genero']
            player.pierna_dominante = data['pierna_dominante']
            player.mano_dominante = data['mano_dominante']
            player.altura = int(float(data['altura'])) if data.get('altura') else None
            player.peso = int(data['peso']) if data.get('peso') else None
            player.ciudad = data.get('ciudad')
            player.telefono = data.get('telefono')

            db.session.add(player)

            print("✅ Datos del jugador actualizados")
            user.is_profile_completed = True
            print("✅ Perfil marcado como completado")

            # Imagen - CORREGIDO: Definir url antes de usarla
            print("🖼️ Procesando imágenes...")
            Imagen.query.filter_by(player_id=player.id).delete()
            print("🗑️ Imágenes anteriores eliminadas")
            
            urls = data.get('profilePicture', [])
            print(f"📸 URLs de imágenes a guardar: {urls}")
            
            for idx, url in enumerate(urls):
                print(f"💾 Guardando imagen {idx + 1}: {url}")
                db.session.add(Imagen(
                    player_id=player.id,
                    url_imagen=url,
                    orden=idx,
                    fecha_creacion=datetime.utcnow()
                ))

            print("💾 Guardando cambios en la base de datos...")
            db.session.commit()
            print("✅ Cambios guardados exitosamente")

            print("🔍 Obteniendo imagen de perfil principal...")
            imagen = Imagen.query.filter_by(player_id=player.id).order_by(Imagen.orden).first()
            url = imagen.url_imagen if imagen else None  # ✅ DEFINIR url AQUÍ
            print(f"📷 URL de imagen de perfil: {url}")

            print("🎉 Perfil de jugador creado/actualizado exitosamente!")
            return {
                'player': {
                    **player.to_dict(),
                    'profilePicture': url  # ✅ Ahora url está definida
                },
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
            print(f"❌ ERROR inesperado al crear perfil de jugador: {str(e)}")
            raise e
        

    @staticmethod
    def get_profile(user_id: int) -> dict:
        player = Player.query.filter_by(user_id=user_id).first()
        if not player:
            raise ValueError("Perfil de jugador no encontrado")

        user = User.query.get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        imagen = Imagen.query.filter_by(player_id=player.id).order_by(Imagen.orden).first()
        url = imagen.url_imagen if imagen else None

        return {
            'player': {
                **player.to_dict(),
                'profilePicture': url
            },
            'user': {
                'id': user.id,
                'email': user.email,
                'is_profile_completed': user.is_profile_completed
            }
        }


