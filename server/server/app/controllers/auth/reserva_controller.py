from flask import request
from app.models.reserva import Reserva
from app.utils.auth_utils import obtener_usuario_desde_token 
from datetime import datetime
from flask_restx import Resource, fields

# Importar namespace y modelos desde el init
from . import (
    reserva_ns, 
    reserva_model, 
    reserva_response_model, 
    horarios_ocupados_response, 
    reserva_verificada_model, 
    reserva_usuario_model,
    reserva_cancelada_response_model,
    error_response_model
)
from app.services.auth.reserva_service import ReservaService

@reserva_ns.route('/crear')
class CrearReservaController(Resource):
    @reserva_ns.expect(reserva_model)
    @reserva_ns.response(201, 'Reserva creada exitosamente', reserva_response_model)
    @reserva_ns.response(400, 'Error de validación', error_response_model)
    @reserva_ns.response(401, 'No autorizado', error_response_model)
    @reserva_ns.response(500, 'Error interno del servidor', error_response_model)
    def post(self):
        """Crear una nueva reserva"""
        try:
            print("🎯 Llegó request a /reserva/crear POST")
            reserva = ReservaService.crear_reserva(request.json)
            
            return {
                "message": "Reserva realizada correctamente",
                "reserva": reserva.to_dict()
            }, 201
            
        except PermissionError as e:
            print(f"❌ Error de permisos: {str(e)}")
            return {"error": str(e)}, 401
        except ValueError as e:
            print(f"❌ Error de validación: {str(e)}")
            return {"error": str(e)}, 400
        except Exception as e:
            print(f"💥 Error interno: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": "Error interno del servidor"}, 500

@reserva_ns.route('/ocupados/<int:cancha_id>/<string:fecha>')
class HorariosOcupadosController(Resource):
    @reserva_ns.response(200, 'Horarios ocupados obtenidos', horarios_ocupados_response)
    @reserva_ns.response(400, 'Parámetros inválidos', error_response_model)
    @reserva_ns.response(500, 'Error interno del servidor', error_response_model)
    def get(self, cancha_id, fecha):
        """Obtener horarios ocupados para una cancha en una fecha específica (por ruta)"""
        print(f"🎯 Llegó request a /reserva/ocupados/{cancha_id}/{fecha} GET")
        
        try:
            fecha_date = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            return {"error": "Formato de fecha inválido (debe ser YYYY-MM-DD)"}, 400

        reservas = Reserva.query.filter_by(cancha_id=cancha_id, fecha=fecha_date).all()
        horas_ocupadas = [r.hora.strftime('%H:%M') for r in reservas]

        return {"horarios_ocupados": horas_ocupadas}, 200

@reserva_ns.route('/ya-reservado')
class VerificarReservaUsuario(Resource):
    @reserva_ns.doc(params={
        'fecha': {'description': 'Fecha en formato YYYY-MM-DD', 'required': True}
    })
    @reserva_ns.response(200, 'Estado de reserva obtenido', reserva_verificada_model)
    @reserva_ns.response(400, 'Parámetros inválidos', error_response_model)
    @reserva_ns.response(401, 'No autorizado', error_response_model)
    @reserva_ns.response(500, 'Error interno del servidor', error_response_model)
    def get(self):
        """Verificar si el usuario ya tiene una reserva para una fecha específica"""
        print("🎯 Llegó request a /reserva/ya-reservado GET")
        
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
    @reserva_ns.response(200, 'Lista de reservas obtenida', fields.List(fields.Nested(reserva_usuario_model)))
    @reserva_ns.response(401, 'No autorizado', error_response_model)
    @reserva_ns.response(500, 'Error interno del servidor', error_response_model)
    def get(self):
        """Obtener TODAS las reservas del usuario autenticado"""
        print("🎯 Llegó request a /reserva/mis-reservas GET - TODAS las reservas")
        
        try:
            # Usar el servicio simplificado
            reservas = ReservaService.obtener_todas_las_reservas_usuario()
            return reservas, 200
            
        except PermissionError as e:
            print(f"❌ Error de autenticación: {str(e)}")
            return {"error": str(e)}, 401
        except Exception as e:
            print(f"💥 Error interno: {str(e)}")
            return {"error": "Error interno del servidor"}, 500

@reserva_ns.route('/cancelar/<int:reserva_id>')
class CancelarReservaController(Resource):
    @reserva_ns.response(200, 'Reserva cancelada exitosamente', reserva_cancelada_response_model)
    @reserva_ns.response(400, 'No se puede cancelar la reserva', error_response_model)
    @reserva_ns.response(401, 'No autorizado', error_response_model)
    @reserva_ns.response(404, 'Reserva no encontrada', error_response_model)
    @reserva_ns.response(500, 'Error interno del servidor', error_response_model)
    def delete(self, reserva_id):
        """Cancelar una reserva específica del usuario"""
        print(f"🎯 Llegó request a /reserva/cancelar/{reserva_id} DELETE")
        
        try:
            resultado = ReservaService.cancelar_reserva(reserva_id)
            return {
                "message": "Reserva cancelada exitosamente",
                "reserva": resultado
            }, 200
            
        except PermissionError as e:
            print(f"❌ Error de permisos: {str(e)}")
            return {"error": str(e)}, 401
        except ValueError as e:
            print(f"❌ Error de validación: {str(e)}")
            return {"error": str(e)}, 400
        except Exception as e:
            print(f"💥 Error interno: {str(e)}")
            return {"error": "Error interno del servidor"}, 500