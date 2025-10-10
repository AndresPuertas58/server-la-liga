from flask import request
from app.models.reserva import Reserva
from app.utils.auth_utils import obtener_usuario_desde_token 
from datetime import datetime

from flask_restx import Namespace, Resource, fields
from app.services.reserva_service import ReservaService

reserva_ns = Namespace('reserva', description='Operaciones de reserva')

reserva_model = reserva_ns.model('Reserva', {
    'cancha_id': fields.Integer(required=True),
    'fecha': fields.String(required=True, description='Formato YYYY-MM-DD'),
    'hora': fields.String(required=True, description='Formato HH:MM (24h)')
})

@reserva_ns.route('/')
class CrearReservaController(Resource):
    
    @reserva_ns.expect(reserva_model)
    def post(self):
        try:
            reserva = ReservaService.crear_reserva(request.json)
            return {
                "message": "Reserva realizada correctamente",
                "reserva": reserva.to_dict()
            }, 201
        except PermissionError as e:
            return {"error": str(e)}, 401
        except ValueError as e:
            return {"error": str(e)}, 400


@reserva_ns.route('/ocupados')
class HorariosOcupadosController(Resource):
    def get(self):
        from datetime import datetime
        from app.models.reserva import Reserva

        cancha_id = request.args.get('cancha_id', type=int)
        fecha_str = request.args.get('fecha')

        if not cancha_id or not fecha_str:
            return {"error": "Parámetros 'cancha_id' y 'fecha' son requeridos"}, 400

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return {"error": "Formato de fecha inválido (debe ser YYYY-MM-DD)"}, 400

        reservas = Reserva.query.filter_by(cancha_id=cancha_id, fecha=fecha).all()
        horas_ocupadas = [r.hora.strftime('%H:%M') for r in reservas]

        return horas_ocupadas, 200



@reserva_ns.route('/ya-reservado')
class VerificarReservaUsuario(Resource):
    def get(self):
        usuario, error, status = obtener_usuario_desde_token()
        if error:
            return error, status

        fecha_str = request.args.get('fecha')
        if not fecha_str:
            return {"error": "Parámetro 'fecha' requerido"}, 400

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return {"error": "Formato de fecha inválido (debe ser YYYY-MM-DD)"}, 400

        reserva = Reserva.query.filter_by(user_id=usuario.id, fecha=fecha).first()
        return {"reservado": bool(reserva)}, 200



@reserva_ns.route('/mis-reservas')
class MisReservasController(Resource):
    def get(self):
        from flask import session, request

        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Usuario no autenticado"}, 401

        cancha_id = request.args.get('cancha_id')
        fecha = request.args.get('fecha')

        if not cancha_id or not fecha:
            return {"error": "Faltan parámetros"}, 400

        reserva_existente = Reserva.query.filter_by(
            user_id=user_id,
            cancha_id=cancha_id,
            fecha=fecha
        ).first()

        return {"tiene_reserva": reserva_existente is not None}, 200

