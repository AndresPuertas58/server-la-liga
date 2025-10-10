from app.utils.database import db
from datetime import datetime

class Reserva(db.Model):
    __tablename__ = 'reservas'

    id = db.Column(db.Integer, primary_key=True)
    cancha_id = db.Column(db.Integer, db.ForeignKey('canchas.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)

    estado = db.Column(db.Enum('pendiente', 'confirmada', 'cancelada'), default='pendiente', nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones (opcional si quieres navegar desde la reserva)
    cancha = db.relationship('Cancha', backref='reservas', lazy=True)
    usuario = db.relationship('User', backref='reservas', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "cancha_id": self.cancha_id,
            "user_id": self.user_id,
            "fecha": self.fecha.isoformat(),
            "hora": self.hora.strftime('%H:%M'),
            "estado": self.estado
        }
