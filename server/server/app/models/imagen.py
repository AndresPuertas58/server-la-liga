# app/models/imagen.py
from app.utils.database import db
from datetime import datetime

class Imagen(db.Model):
    __tablename__ = 'imagenes'

    id = db.Column(db.Integer, primary_key=True)
    cancha_id = db.Column(db.Integer, db.ForeignKey('canchas.id'), nullable=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=True)
    url_imagen = db.Column(db.String(255), nullable=False)
    orden = db.Column(db.Integer, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)


