from flask import make_response, jsonify

def logout_user():
    response = make_response(jsonify({'message': 'Sesión cerrada exitosamente'}))
    response.set_cookie(
        'liga_token',
        '',
        expires=0,
        httponly=True,
        secure=False,  # False para desarrollo
        samesite='Lax'
    )
    return response