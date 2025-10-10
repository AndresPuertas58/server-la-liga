from app.models.reserva import Reserva
from app.models.cancha import Cancha
from app.models.user_model import UserRole
from app.models.dia_festivo import DiaFestivo
from app.utils.database import db
from app.utils.auth_utils import obtener_usuario_desde_token
from datetime import datetime
import calendar

class ReservaService:

    @staticmethod
    def crear_reserva(data):
        # Obtener usuario autenticado desde el token
        usuario, error, status = obtener_usuario_desde_token()
        if error:
            raise PermissionError("Usuario no autenticado")

        
        fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()

        reserva_existente = Reserva.query.filter_by(user_id=usuario.id, fecha=fecha).first()
        if reserva_existente:
            raise ValueError("Ya tienes una reserva para este día, solo puedes reservar una hora al dia.")

        hora = datetime.strptime(data['hora'], '%H:%M').time().replace(second=0)
        cancha_id = data['cancha_id']

        # Verificar si la cancha existe
        cancha = Cancha.query.get(cancha_id)
        if not cancha:
            raise ValueError("Cancha no encontrada")

        # Verificar si ya existe una reserva en ese horario
        reserva_existente = Reserva.query.filter_by(
            cancha_id=cancha_id,
            fecha=fecha,
            hora=hora
        ).first()
        if reserva_existente:
            raise ValueError("Ya existe una reserva en ese horario")

        # Determinar tipo de día (festivo, fin de semana, entre semana)
        festivo = DiaFestivo.query.filter_by(fecha=fecha).first()
        if festivo and not festivo.es_laborable:
            tipo_dia = 'domingo'  # horario especial para no laborables
        else:
            dia_semana = calendar.day_name[fecha.weekday()].lower()
            dias_map = {
                'monday': 'lunes',
                'tuesday': 'martes',
                'wednesday': 'miercoles',
                'thursday': 'jueves',
                'friday': 'viernes',
                'saturday': 'sabado',
                'sunday': 'domingo'
            }
            tipo_dia = dias_map.get(dia_semana)

        # Buscar horarios permitidos para ese día
        horarios_disponibles = [
            h.hora.replace(second=0)
            for h in cancha.horarios
            if h.dia_semana == tipo_dia
        ]

        if hora not in horarios_disponibles:
            raise ValueError(f"La hora {hora.strftime('%H:%M')} no está disponible para {tipo_dia}")

        # Crear reserva
        nueva_reserva = Reserva(
            cancha_id=cancha_id,
            user_id=usuario.id,
            fecha=fecha,
            hora=hora,
            estado='pendiente'
        )

        db.session.add(nueva_reserva)
        db.session.commit()
        return nueva_reserva
