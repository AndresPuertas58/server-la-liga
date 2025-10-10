from app.utils.database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    is_profile_completed = db.Column(db.Boolean, default=False)
    terms = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    status=db.Column(db.Boolean, default=True)
    name_user=db.Column(db.String(255), nullable=False)


    def __repr__(self):
        return f'<User {self.email}>'