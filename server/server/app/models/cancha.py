# app/models/cancha.py

from app.utils.database import db
from datetime import datetime
from app.models.imagen import Imagen  # Asegúrate de importar el modelo correcto

class Cancha(db.Model):
    __tablename__ = 'canchas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    subtipo = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    latitud = db.Column(db.Numeric(10, 8), nullable=False)
    longitud = db.Column(db.Numeric(11, 8), nullable=False)
    direccion_completa = db.Column(db.Text, nullable=False)
    superficie = db.Column(db.String(50), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    precio_hora = db.Column(db.Numeric(10, 2), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    estado = db.Column(db.Enum('activa', 'inactiva', 'en_mantenimiento'), default='activa')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # ✅ Relaciones
    imagenes = db.relationship(
        'Imagen',
        primaryjoin="Cancha.id == foreign(Imagen.cancha_id)",
        backref='cancha',
        lazy=True,
        cascade="all, delete-orphan"
    )
    horarios = db.relationship('HorarioCancha', backref='cancha', lazy=True, cascade="all, delete-orphan")
    reglas = db.relationship('ReglaCancha', backref='cancha', lazy=True, cascade="all, delete-orphan")
    amenidades = db.relationship('AmenidadCancha', backref='cancha', lazy=True, cascade="all, delete-orphan")

    # ✅ Método de serialización
    def to_dict_completo(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'subtipo': self.subtipo,
            'direccion': self.direccion,
            'latitud': float(self.latitud),
            'longitud': float(self.longitud),
            'direccion_completa': self.direccion_completa,
            'superficie': self.superficie,
            'capacidad': self.capacidad,
            'precio_hora': float(self.precio_hora),
            'descripcion': self.descripcion,
            'estado': self.estado,
            'imagenes': [
                {
                    'id': img.id,
                    'url': img.url_imagen,
                    'orden': img.orden,
                    'fecha_creacion': img.fecha_creacion.isoformat()
                } for img in sorted(self.imagenes, key=lambda x: x.orden or 0)
            ],
            'horarios': [
                {
                    'dia_semana': h.dia_semana,
                    'hora': h.hora.strftime('%H:%M') if h.hora else None
                } for h in self.horarios
            ],
            'reglas': [r.regla for r in self.reglas],
            'amenidades': [a.amenidad for a in self.amenidades]
        }
