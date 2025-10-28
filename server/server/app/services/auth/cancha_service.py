from flask import session
from datetime import datetime, time, timedelta
from app.models.cancha import Cancha
from app.models.imagen import Imagen
from app.models.horario_cancha import HorarioCancha
from app.models.regla_cancha import ReglaCancha
from app.models.amenidad_cancha import AmenidadCancha
from app.utils.database import db
from app.utils.auth_utils import obtener_usuario_desde_token
from app.models.dia_festivo import DiaFestivo
from app.models.reserva import Reserva
from sqlalchemy import Numeric
import calendar

class CanchaService:

    @staticmethod
    def crear_cancha_con_todo(data):
        print("🔍 Iniciando creación de cancha en servicio...")
        
        usuario, error, status = obtener_usuario_desde_token()
        print(f"👤 Usuario desde token: {usuario}")
        
        if error:
            print("❌ Usuario no autenticado")
            raise PermissionError("Usuario no autenticado")
        
        print(f"✅ Usuario autenticado: {usuario.email}, Role: {usuario.role}")

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
            estado=data.get('estado', 'activa')
        )

        db.session.add(cancha)
        db.session.flush()  # Para obtener el ID sin hacer commit

        # Imágenes
        for i, url in enumerate(data.get('imagenes', [])):
            imagen = Imagen(cancha_id=cancha.id, url_imagen=url, orden=i)
            db.session.add(imagen)
            print(f"📸 Imagen recibida {url}")

        # HORARIOS - NUEVO FORMATO CON RANGOS
        for horario in data.get('horarios', []):
            h = HorarioCancha(
                cancha_id=cancha.id,
                dia_semana=horario['dia_semana'],
                hora_inicio=datetime.strptime(horario['hora_inicio'], '%H:%M').time(),
                hora_fin=datetime.strptime(horario['hora_fin'], '%H:%M').time(),
                intervalo_minutos=horario.get('intervalo_minutos', 60),
                disponible=horario.get('disponible', True)
            )
            db.session.add(h)
            print(f"🕒 Horario agregado: {horario['dia_semana']} {horario['hora_inicio']}-{horario['hora_fin']} (intervalo: {h.intervalo_minutos}min)")

        # Reglas
        for regla in data.get('reglas', []):
            r = ReglaCancha(
                cancha_id=cancha.id,
                regla=regla['regla'],
            )
            db.session.add(r)
            print(f"📏 Regla agregada: {regla['regla']}")

        # Amenidades
        for amenidad in data.get('amenidades', []):
            a = AmenidadCancha(
                cancha_id=cancha.id,
                amenidad=amenidad['amenidad'],
            )
            db.session.add(a)
            print(f"🏆 Amenidad agregada: {amenidad['amenidad']}")

        db.session.commit()
        print("✅ Cancha creada exitosamente")
        return cancha
    

    @staticmethod
    def obtener_cancha_por_id(cancha_id):
        print(f"🔍 Buscando cancha ID: {cancha_id}")
        cancha = Cancha.query.get(cancha_id)
        if cancha:
            print(f"✅ Cancha encontrada: {cancha.nombre}")
        else:
            print("❌ Cancha no encontrada")
        return cancha

    @staticmethod
    def obtener_todas_las_canchas():
        print("🔍 Obteniendo todas las canchas activas")
        canchas = Cancha.query.filter_by(estado='activa').all()
        print(f"✅ Encontradas {len(canchas)} canchas activas")
        return canchas
    

    @staticmethod
    def obtener_horarios_disponibles(cancha_id: int, fecha_str: str):
        print(f"🔍 Obteniendo horarios disponibles para cancha {cancha_id} en fecha {fecha_str}")
        
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

        # Verificar si es festivo
        festivo = DiaFestivo.query.filter_by(fecha=fecha).first()
        if festivo:
            tipo_dia = 'domingo'  # O el tipo que uses para festivos
            print(f"🎉 Fecha {fecha_str} es festivo, se usa tipo: {tipo_dia}")
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
            print(f"📅 Fecha {fecha_str} es {tipo_dia}")

        # Obtener horarios de ese día para la cancha (NUEVO: rangos)
        horarios_rango = HorarioCancha.query.filter_by(
            cancha_id=cancha_id, 
            dia_semana=tipo_dia,
            disponible=True
        ).all()

        # Generar todos los horarios disponibles desde los rangos
        todos_horarios_disponibles = set()
        for horario_rango in horarios_rango:
            horarios_generados = CanchaService._generar_horarios_desde_rango(
                horario_rango.hora_inicio, 
                horario_rango.hora_fin, 
                horario_rango.intervalo_minutos
            )
            todos_horarios_disponibles.update(horarios_generados)
        
        print(f"🕒 Horarios configurados: {sorted(todos_horarios_disponibles)}")

        # Obtener reservas ya hechas para esa cancha en esa fecha
        reservas = Reserva.query.filter_by(cancha_id=cancha_id, fecha=fecha).all()
        horas_reservadas = {r.hora.strftime('%H:%M') for r in reservas}
        print(f"🔒 Horarios reservados: {sorted(horas_reservadas)}")

        # Calcular horarios disponibles
        disponibles = sorted(todos_horarios_disponibles - horas_reservadas)
        print(f"✅ Horarios disponibles: {disponibles}")

        return disponibles

    @staticmethod
    def _generar_horarios_desde_rango(hora_inicio: time, hora_fin: time, intervalo_minutos: int):
        """
        Generar lista de horarios basado en un rango y intervalo
        """
        horarios = []
        current_time = datetime.combine(datetime.today(), hora_inicio)
        end_time = datetime.combine(datetime.today(), hora_fin)

        while current_time < end_time:
            horarios.append(current_time.time().strftime('%H:%M'))
            current_time += timedelta(minutes=intervalo_minutos)

        return horarios

    @staticmethod
    def verificar_disponibilidad_horario(cancha_id: int, dia_semana: str, hora_solicitada: str):
        """
        Verificar si un horario específico está disponible según los rangos configurados
        """
        hora_time = datetime.strptime(hora_solicitada, '%H:%M').time()
        
        horarios_disponibles = HorarioCancha.query.filter_by(
            cancha_id=cancha_id,
            dia_semana=dia_semana,
            disponible=True
        ).all()

        for horario in horarios_disponibles:
            if CanchaService._hora_en_rango(hora_time, horario.hora_inicio, horario.hora_fin, horario.intervalo_minutos):
                return True
        
        return False

    @staticmethod
    def _hora_en_rango(hora_solicitada: time, hora_inicio: time, hora_fin: time, intervalo_minutos: int):
        """
        Verificar si una hora específica está dentro de un rango considerando el intervalo
        """
        hora_solicitada_dt = datetime.combine(datetime.today(), hora_solicitada)
        inicio_dt = datetime.combine(datetime.today(), hora_inicio)
        fin_dt = datetime.combine(datetime.today(), hora_fin)

        # Verificar que esté dentro del rango general
        if not (inicio_dt <= hora_solicitada_dt < fin_dt):
            return False

        # Verificar que coincida con el intervalo
        tiempo_desde_inicio = hora_solicitada_dt - inicio_dt
        minutos_desde_inicio = tiempo_desde_inicio.total_seconds() / 60
        
        return minutos_desde_inicio % intervalo_minutos == 0