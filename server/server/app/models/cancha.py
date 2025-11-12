from app.utils.database import db
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Numeric
from flask import request, current_app  # ✅ Agregar current_app aquí
import os
import base64

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

    def to_dict_con_imagenes_base64(self):
        """
        Incluir las imágenes completas en base64
        """
        data = self.to_dict_completo()
        
        # Reemplazar las URLs por datos base64
        data['imagenes_base64'] = []
        
        for img in self.imagenes:
            if img.url_imagen.startswith('/utils/pictures/'):
                # Es una imagen local, cargar como base64
                base64_data = self._cargar_imagen_a_base64(img.url_imagen)
                if base64_data:
                    data['imagenes_base64'].append({
                        'id': img.id,
                        'orden': img.orden,
                        'data': base64_data,
                        'nombre': os.path.basename(img.url_imagen),
                        'tipo': 'local'
                    })
                else:
                    # Si no se pudo cargar, mantener la URL original
                    data['imagenes_base64'].append({
                        'id': img.id,
                        'orden': img.orden,
                        'url': img.url_imagen,
                        'tipo': 'local_error'
                    })
            else:
                # Es una URL externa, mantener como URL
                data['imagenes_base64'].append({
                    'id': img.id,
                    'orden': img.orden,
                    'url': img.url_imagen,
                    'tipo': 'externo'
                })
        
        return data

    def _cargar_imagen_a_base64(self, ruta_imagen):
        """
        Cargar imagen del sistema de archivos y convertir a base64
        """
        try:
            # Construir ruta completa
            if ruta_imagen.startswith('/'):
                ruta_completa = os.path.join(current_app.root_path, ruta_imagen.lstrip('/'))
            else:
                ruta_completa = os.path.join(current_app.root_path, 'utils', 'pictures', 'canchas', str(self.id), ruta_imagen)
            
            print(f"📁 Intentando cargar imagen: {ruta_completa}")
            
            # Verificar que el archivo existe
            if not os.path.exists(ruta_completa):
                print(f"❌ Imagen no encontrada: {ruta_completa}")
                return None
            
            # Leer imagen y convertir a base64
            with open(ruta_completa, 'rb') as img_file:
                imagen_bytes = img_file.read()
                base64_encoded = base64.b64encode(imagen_bytes).decode('utf-8')
                
                # Determinar el tipo MIME
                extension = os.path.splitext(ruta_completa)[1].lower()
                mime_types = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }
                mime_type = mime_types.get(extension, 'image/jpeg')
                
                print(f"✅ Imagen convertida a base64: {os.path.basename(ruta_imagen)}")
                return f"data:{mime_type};base64,{base64_encoded}"
                
        except Exception as e:
            print(f"❌ Error cargando imagen a base64: {str(e)}")
            return None