# app/models/dia_festivo.py

from app.utils.database import db

class DiaFestivo(db.Model):
    __tablename__ = 'dias_festivos'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, unique=True, nullable=False, comment="Fecha exacta del día festivo")
    descripcion = db.Column(db.String(100), default=None)
    es_laborable = db.Column(db.Boolean, default=False, nullable=False, comment="0 = No se trabaja, 1 = Sí se trabaja")
