from app.utils.database import db
from datetime import datetime, time
from sqlalchemy import event

class HorarioCancha(db.Model):
    __tablename__ = 'horarios_cancha'

    id = db.Column(db.Integer, primary_key=True)
    cancha_id = db.Column(db.Integer, db.ForeignKey('canchas.id'), nullable=False)
    dia_semana = db.Column(
        db.Enum('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'), 
        nullable=False
    )
    hora_inicio = db.Column(db.Time, nullable=False, comment='Ejemplo: 10:00:00')
    hora_fin = db.Column(db.Time, nullable=False, comment='Ejemplo: 23:00:00')
    intervalo_minutos = db.Column(db.Integer, default=60, comment='Cada cuántos minutos se puede reservar')
    disponible = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.TIMESTAMP, default=datetime.now)

    def __repr__(self):
        return f'<HorarioCancha {self.dia_semana} {self.hora_inicio}-{self.hora_fin}>'

    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'cancha_id': self.cancha_id,
            'dia_semana': self.dia_semana,
            'hora_inicio': self.hora_inicio.strftime('%H:%M') if self.hora_inicio else None,
            'hora_fin': self.hora_fin.strftime('%H:%M') if self.hora_fin else None,
            'intervalo_minutos': self.intervalo_minutos,
            'disponible': self.disponible,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

    def generar_horarios_disponibles(self):
        """
        Generar lista de horarios disponibles basado en el rango y intervalo
        """
        if not self.disponible:
            return []

        horarios = []
        current_time = datetime.combine(datetime.today(), self.hora_inicio)
        end_time = datetime.combine(datetime.today(), self.hora_fin)

        while current_time < end_time:
            horarios.append(current_time.time().strftime('%H:%M'))
            current_time = current_time + timedelta(minutes=self.intervalo_minutos)

        return horarios

    def esta_disponible_para_hora(self, hora_solicitada):
        """
        Verificar si una hora específica está dentro del rango disponible
        """
        if not self.disponible:
            return False

        hora_solicitada_dt = datetime.combine(datetime.today(), hora_solicitada)
        inicio_dt = datetime.combine(datetime.today(), self.hora_inicio)
        fin_dt = datetime.combine(datetime.today(), self.hora_fin)

        return inicio_dt <= hora_solicitada_dt < fin_dt

# Evento para validar que hora_fin sea mayor que hora_inicio
@event.listens_for(HorarioCancha, 'before_insert')
@event.listens_for(HorarioCancha, 'before_update')
def validate_time_range(mapper, connection, target):
    if target.hora_inicio and target.hora_fin:
        if target.hora_inicio >= target.hora_fin:
            raise ValueError("hora_fin debe ser mayor que hora_inicio")