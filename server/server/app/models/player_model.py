# app/models/player_model.py
from app.utils.database import db
from enum import Enum

class Genero(str, Enum):
    masculino = "masculino"
    femenino = "femenino"
    otro = "otro"

class LadoDominante(str, Enum):
    izquierda = "izquierda"
    derecha = "derecha"
    ambas = "ambas"

class EstadoJugador(str, Enum):
    activo = "activo"
    inactivo = "inactivo"
    lesion = "lesion"

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    deporte = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(255), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    posicion = db.Column(db.String(255), nullable=False)
    pierna_dominante = db.Column(db.Enum(LadoDominante), nullable=True)
    mano_dominante = db.Column(db.Enum(LadoDominante), nullable=True)
    genero = db.Column(db.Enum(Genero), nullable=True)
    altura = db.Column(db.Integer)  # cm
    peso = db.Column(db.Integer)    # kg
    estado = db.Column(db.Enum(EstadoJugador), nullable=True)
    ciudad = db.Column(db.String(255), nullable=True)     # 🆕
    telefono = db.Column(db.String(20), nullable=True)     # 🆕
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())
    fecha_actualizacion = db.Column(db.DateTime, onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'nombre_completo': self.nombre_completo,
            'deporte': self.deporte,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'posicion': self.posicion,
            'pierna_dominante': self.pierna_dominante.value if self.pierna_dominante else None,
            'mano_dominante': self.mano_dominante.value if self.mano_dominante else None,
            'genero': self.genero.value if self.genero else None,
            'altura': self.altura,
            'peso': self.peso,
            'estado': self.estado.value if self.estado else None,
            'ciudad': self.ciudad,
            'telefono': self.telefono,
        }
