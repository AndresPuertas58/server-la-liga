from app.utils.database import db
from datetime import datetime
from decimal import Decimal

class Reserva(db.Model):
    __tablename__ = 'reservas'
    
    id = db.Column(db.Integer, primary_key=True)
    cancha_id = db.Column(db.Integer, db.ForeignKey('canchas.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    cancha = db.relationship('Cancha', backref='reservas')
    usuario = db.relationship('User', backref='reservas')
    
    def to_dict(self):
        # Convertir Decimal a float para serialización JSON
        precio_hora = None
        if self.cancha and self.cancha.precio_hora:
            # Convertir Decimal a float
            if isinstance(self.cancha.precio_hora, Decimal):
                precio_hora = float(self.cancha.precio_hora)
            else:
                precio_hora = float(self.cancha.precio_hora)
        
        return {
            'id': self.id,
            'cancha_id': self.cancha_id,
            'user_id': self.user_id,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'hora': self.hora.strftime('%H:%M') if self.hora else None,
            'estado': self.estado,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'cancha': {
                'id': self.cancha.id,
                'nombre': self.cancha.nombre,
                'tipo': self.cancha.tipo,
                'precio_hora': precio_hora
            } if self.cancha else None
        }