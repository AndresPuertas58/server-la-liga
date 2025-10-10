from app.utils.database import db

class Owner(db.Model):
    __tablename__ = 'owners'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    nombre_administrador = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'nombre_administrador': self.nombre_administrador,
            'telefono': self.telefono,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }