from app.utils.database import db
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Numeric  # ✅ Importar Numeric de SQLAlchemy

class Cancha(db.Model):
    __tablename__ = 'canchas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    subtipo = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    direccion_completa = db.Column(db.String(300), nullable=False)
    superficie = db.Column(db.String(50), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    precio_hora = db.Column(Numeric(10, 2), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), default='activa')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    imagenes = db.relationship('Imagen', backref='cancha', lazy=True, cascade='all, delete-orphan')
    
    # ✅ SOLUCIÓN: Esta relación debe apuntar al nuevo modelo HorarioCancha
    horarios = db.relationship('HorarioCancha', backref='cancha', lazy=True, cascade='all, delete-orphan')
    
    reglas = db.relationship('ReglaCancha', backref='cancha', lazy=True, cascade='all, delete-orphan')
    amenidades = db.relationship('AmenidadCancha', backref='cancha', lazy=True, cascade='all, delete-orphan')
    
    def to_dict_completo(self):
        # Convertir Numeric/Decimal a float para JSON
        precio_hora_float = float(self.precio_hora) if self.precio_hora else None
        
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'subtipo': self.subtipo,
            'direccion': self.direccion,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'direccion_completa': self.direccion_completa,
            'superficie': self.superficie,
            'capacidad': self.capacidad,
            'precio_hora': precio_hora_float,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'imagenes': [img.url_imagen for img in self.imagenes],
            # ✅ ACTUALIZAR: Usar los nuevos campos de horarios
            'horarios': [{
                'dia_semana': h.dia_semana, 
                'hora_inicio': h.hora_inicio.strftime('%H:%M'),
                'hora_fin': h.hora_fin.strftime('%H:%M'),
                'intervalo_minutos': h.intervalo_minutos,
                'disponible': h.disponible
            } for h in self.horarios],
            'reglas': [{'regla': r.regla} for r in self.reglas],
            'amenidades': [{'amenidad': a.amenidad} for a in self.amenidades]
        }