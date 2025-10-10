from flask import session
from datetime import datetime
from app.models.cancha import Cancha
from app.models.imagen import Imagen
from app.models.horario_cancha import HorarioCancha
from app.models.regla_cancha import ReglaCancha
from app.models.amenidad_cancha import AmenidadCancha
from app.utils.database import db
from app.utils.auth_utils import obtener_usuario_desde_token


from datetime import datetime
from app.models.dia_festivo import DiaFestivo
from app.models.reserva import Reserva
from app.models.horario_cancha import HorarioCancha
from sqlalchemy import and_
import calendar



class CanchaService:

    @staticmethod
    def crear_cancha_con_todo(data):
        print("🔍 Iniciando creación de cancha en servicio...")
        
        usuario, error, status = obtener_usuario_desde_token()
        print(f"👤 Usuario desde token: {usuario}")
        print(f"❌ Error: {error}")
        print(f"📊 Status: {status}")
        
        if error:
            print("❌ Usuario no autenticado")
            raise PermissionError("Usuario no autenticado")
        
        print(f"✅ Usuario autenticado: {usuario.email}, Role: {usuario.role.value}")
        
        # Verificar que el usuario es un owner
        if usuario.role.value != 'owner':
            print("❌ Usuario no es owner")
            raise PermissionError("Solo owners pueden crear canchas")
        
        owner_id = usuario.id
        print(f"🏷️ Owner ID: {owner_id}")

        cancha = Cancha(
            nombre=data['nombre'],
            tipo=data['tipo'],
            subtipo=data['subtipo'],
            direccion=data['direccion'],
            latitud=data['latitud'],
            longitud=data['longitud'],
            direccion_completa=data['direccion_completa'],
            superficie=data['superficie'],
            capacidad=data['capacidad'],
            precio_hora=data['precio_hora'],
            descripcion=data['descripcion'],
            estado=data.get('estado', 'activa'),
            owner_id=owner_id
        )

        db.session.add(cancha)
        db.session.flush()  # Para obtener el ID sin hacer commit

        # Imágenes
        for i, url in enumerate(data.get('imagenes', [])):
            imagen = Imagen(cancha_id=cancha.id, url_imagen=url, orden=i)
            db.session.add(imagen)
            print(f"imagen recibida {url}")

        # Horarios
        for horario in data.get('horarios', []):
            h = HorarioCancha(
                cancha_id=cancha.id,
                dia_semana=horario['dia_semana'],
                hora=horario['hora']
            )
            db.session.add(h)

        # Reglas
        for regla in data.get('reglas', []):
            r = ReglaCancha(
                cancha_id=cancha.id,
                regla=regla['regla'],
            )
            db.session.add(r)

        # Amenidades
        for amenidad in data.get('amenidades', []):
            a = AmenidadCancha(
                cancha_id=cancha.id,
                amenidad=amenidad['amenidad'],
            )
            db.session.add(a)

        db.session.commit()
        return cancha
    

    @staticmethod
    def obtener_cancha_por_id(cancha_id):
        return Cancha.query.get(cancha_id)

    @staticmethod
    def obtener_todas_las_canchas():
        return Cancha.query.filter_by(estado='activa').all()
    

    @staticmethod
    def obtener_horarios_disponibles(cancha_id: int, fecha_str: str):
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

         # Verificar si es festivo
        festivo = DiaFestivo.query.filter_by(fecha=fecha).first()
        if festivo:
            tipo_dia = 'domingo'  # O el tipo que uses para festivos
        else:
            dias_map = {
                'monday': 'lunes',
                'tuesday': 'martes',
                'wednesday': 'miercoles',
                'thursday': 'jueves',
                'friday': 'viernes',
                'saturday': 'sabado',
                'sunday': 'domingo'
            }  
            dia_semana = calendar.day_name[fecha.weekday()].lower()
            tipo_dia = dias_map.get(dia_semana)

         # Obtener horarios de ese día para la cancha
        horarios = HorarioCancha.query.filter_by(cancha_id=cancha_id, dia_semana=tipo_dia).all()
        horas_disponibles = {h.hora.strftime('%H:%M') for h in horarios}

        # Obtener reservas ya hechas para esa cancha en esa fecha
        reservas = Reserva.query.filter_by(cancha_id=cancha_id, fecha=fecha).all()
        horas_reservadas = {r.hora.strftime('%H:%M') for r in reservas}

        # Calcular horarios disponibles
        disponibles = sorted(horas_disponibles - horas_reservadas)

        return disponibles


