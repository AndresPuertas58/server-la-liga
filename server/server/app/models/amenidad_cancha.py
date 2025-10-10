# app/models/amenidad_cancha.py
from app.utils.database import db

class AmenidadCancha(db.Model):
    __tablename__ = 'amenidades_cancha'

    id = db.Column(db.Integer, primary_key=True)
    cancha_id = db.Column(db.Integer, db.ForeignKey('canchas.id'), nullable=False)
    amenidad = db.Column(db.String(100), nullable=False)

