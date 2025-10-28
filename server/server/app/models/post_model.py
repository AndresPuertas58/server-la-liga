from app.utils.database import db
from datetime import datetime

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tipo_post = db.Column(db.Enum('texto', 'foto'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    imagen_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    eliminado = db.Column(db.Boolean, default=False)

    # Relaciones
    usuario = db.relationship('User', backref=db.backref('posts', lazy=True))
    comentarios = db.relationship('PostComentario', backref='post', lazy=True)
    likes = db.relationship('PostLike', backref='post', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'tipo_post': self.tipo_post,
            'contenido': self.contenido,
            'imagen_url': self.imagen_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'eliminado': self.eliminado,
            'usuario': {
                'id': self.usuario.id,
                'name_user': self.usuario.name_user,
                'urlphotoperfil': self.usuario.urlphotoperfil
            } if self.usuario else None,
            'total_comentarios': len([c for c in self.comentarios if not c.eliminado]),
            'total_likes': len(self.likes)
        }

class PostComentario(db.Model):
    __tablename__ = 'post_comentarios'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    eliminado = db.Column(db.Boolean, default=False)

    # Relaciones
    usuario = db.relationship('User', backref=db.backref('comentarios', lazy=True))
    likes = db.relationship('ComentarioLike', backref='comentario', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'usuario_id': self.usuario_id,
            'contenido': self.contenido,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'eliminado': self.eliminado,
            'usuario': {
                'id': self.usuario.id,
                'name_user': self.usuario.name_user,
                'urlphotoperfil': self.usuario.urlphotoperfil
            } if self.usuario else None,
            'total_likes': len(self.likes)
        }

class PostLike(db.Model):
    __tablename__ = 'post_likes'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'usuario_id': self.usuario_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ComentarioLike(db.Model):
    __tablename__ = 'comentario_likes'

    id = db.Column(db.Integer, primary_key=True)
    comentario_id = db.Column(db.Integer, db.ForeignKey('post_comentarios.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'comentario_id': self.comentario_id,
            'usuario_id': self.usuario_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }