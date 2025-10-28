from app.utils.database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False, default='user')
    terms = db.Column(db.Boolean, nullable=False)
    is_profile_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    status = db.Column(db.Boolean, default=True, comment='si el usuario esta activo o no')
    name_user = db.Column(db.String(255), nullable=False)
    urlphotoperfil = db.Column(db.String(255), nullable=True)
    telephone = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    sport = db.Column(db.String(255), nullable=True)
    fechanacimiento = db.Column(db.DateTime, nullable=True)
    position = db.Column(db.String(255), nullable=True)
    biography = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<User {self.email}>'