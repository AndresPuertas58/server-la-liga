import re

def validate_registration(data):
    """Valida los datos de registro"""
    errors = []
    
    # Validar name
    if not data.get('name_user'):
        errors.append('El nombre es requerido')
    elif len(data['name_user'].strip()) < 2:
        errors.append('El nombre debe tener al menos 2 caracteres')
    
    # Validar email
    if not data.get('email'):
        errors.append('El email es requerido')
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
        errors.append('El formato del email no es válido')
    
    # Validar password
    if not data.get('password'):
        errors.append('La contraseña es requerida')
    elif len(data['password']) < 6:
        errors.append('La contraseña debe tener al menos 6 caracteres')
    
    return errors


def validate_login(data):
    """Valida los datos de registro"""
    errors = []
    
    # Validar email
    if not data.get('email'):
        errors.append('El email es requerido')
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
        errors.append('El formato del email no es válido')
    
    # Validar password
    if not data.get('password'):
        errors.append('La contraseña es requerida')
    elif len(data['password']) < 6:
        errors.append('La contraseña debe tener al menos 6 caracteres')
    
    return errors   