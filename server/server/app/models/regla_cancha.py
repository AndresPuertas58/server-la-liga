# app/models/regla_cancha.py
from app.utils.database import db

class ReglaCancha(db.Model):
    __tablename__ = 'reglas_cancha'

    id = db.Column(db.Integer, primary_key=True)
    cancha_id = db.Column(db.Integer, db.ForeignKey('canchas.id'), nullable=False)
    regla = db.Column(db.String(100), nullable=False)
