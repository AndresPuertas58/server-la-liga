from werkzeug.exceptions import BadRequest
import re
from app.models.user_model import UserRole

def validate_registration(data):
    errors = {}
    
    if not data.get('email'):
        errors['email'] = "Email es requerido"
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        errors['email'] = "Email inválido"
    
    if not data.get('password'):
        errors['password'] = "Contraseña es requerida"
    elif len(data['password']) < 8:
        errors['password'] = "La contraseña debe tener al menos 8 caracteres"
    
    if not data.get('role'):
        errors['role'] = "Rol es requerido"
    elif data['role'].lower() not in [role.value for role in UserRole]:
        errors['role'] = f"Rol inválido. Debe ser uno de: {[role.value for role in UserRole]}"
    
    if data.get('terms') is not True:
        errors['terms'] = "Debes aceptar los términos y condiciones"
    
    return errors if errors else None

def validate_login(data):
    if not data.get('email') or not data.get('password'):
        raise BadRequest("Email y contraseña son requeridos")