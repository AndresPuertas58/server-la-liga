# app/models/horario_cancha.py
from app.utils.database import db

class HorarioCancha(db.Model):
    __tablename__ = 'horarios_cancha'

    id = db.Column(db.Integer, primary_key=True)
    cancha_id = db.Column(db.Integer, db.ForeignKey('canchas.id'), nullable=False)
    dia_semana = db.Column(db.Enum('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'), nullable=False)
    hora = db.Column(db.Time, nullable=False)
    disponible = db.Column(db.Boolean, default=True)
