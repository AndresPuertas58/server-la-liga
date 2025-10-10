import bcrypt
from app.models.user_model import User
from app.utils.database import db

class AuthService:
    @staticmethod
    def register_user(data):
        # Verificar si el email ya existe
        if User.query.filter_by(email=data['email']).first():
            raise ValueError('El email ya está registrado')

        # Hashear la contraseña
        hashed_password = bcrypt.hashpw(
            data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Asignar rol por defecto (puedes cambiar 'player' por el que prefieras)
        default_role = "player"  # o "owner", "team" según tu lógica de negocio

        # Crear nuevo usuario
        user = User(
            name_user=data['name'],
            email=data['email'],
            password=hashed_password,
            role=default_role,  # Rol asignado automáticamente
            terms=True  # Términos aceptados automáticamente
        )
        db.session.add(user)
        db.session.commit()

        return {
            'message': 'Registro exitoso',
            'user': {
                'id': user.id,
                'name': user.name_user,
                'email': user.email,
                'role': user.role  # Ya no es .value porque es string
            }
        }