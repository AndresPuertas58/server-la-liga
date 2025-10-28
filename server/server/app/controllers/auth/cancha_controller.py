from flask import request
from flask_restx import Resource, fields
from app.services.auth.cancha_service import CanchaService

# Importar namespace y modelos
from . import cancha_ns, cancha_model, cancha_response_model, horarios_disponibles_model

# Ruta para CREAR cancha (POST)
@cancha_ns.route('/create')
class CanchaCreateResource(Resource):
    @cancha_ns.expect(cancha_model)
    @cancha_ns.response(201, 'Cancha creada correctamente')
    @cancha_ns.response(401, 'No autorizado')
    @cancha_ns.response(500, 'Error interno del servidor')
    def post(self):
        """Crear una nueva cancha"""
        print("🎯 Llegó request a /cancha/ POST")
        try:
            data = request.json
            print(f"📥 Datos recibidos: {data}")
            
            cancha = CanchaService.crear_cancha_con_todo(data)
            return {
                'message': 'Cancha creada correctamente',
                'cancha': {
                    'id': cancha.id,
                    'nombre': cancha.nombre,
                    'tipo': cancha.tipo,
                    'estado': cancha.estado
                }
            }, 201
            
        except PermissionError as e:
            print(f"❌ Error de permisos: {str(e)}")
            return {"message": "No autorizado - token inválido o expirado"}, 401
        except Exception as e:
            print(f"❌ Error interno: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"message": "Error interno del servidor"}, 500

# Ruta para OBTENER todas las canchas (GET)
@cancha_ns.route('/list')
class CanchaListResource(Resource):
    @cancha_ns.response(200, 'Lista de canchas obtenida', fields.List(fields.Nested(cancha_response_model)))
    @cancha_ns.response(500, 'Error al obtener canchas')
    def get(self):
        """Obtener todas las canchas activas"""
        print("🎯 Llegó request a /cancha/list GET")
        try:
            canchas = CanchaService.obtener_todas_las_canchas()
            return [c.to_dict_completo() for c in canchas], 200
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"message": "Error al obtener canchas"}, 500

# Ruta para OBTENER cancha por ID (GET)
@cancha_ns.route('/<int:id>')
class CanchaDetailResource(Resource):
    @cancha_ns.response(200, 'Cancha encontrada', cancha_response_model)
    @cancha_ns.response(404, 'Cancha no encontrada')
    @cancha_ns.response(500, 'Error al obtener cancha')
    def get(self, id):
        """Obtener cancha por ID"""
        print(f"🎯 Llegó request a /cancha/{id} GET")
        try:
            cancha = CanchaService.obtener_cancha_por_id(id)
            if not cancha:
                return {"message": "Cancha no encontrada"}, 404
            return cancha.to_dict_completo(), 200
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"message": "Error al obtener cancha"}, 500

# Ruta para horarios disponibles
@cancha_ns.route('/<int:cancha_id>/horarios-disponibles')
class HorariosDisponiblesResource(Resource):
    @cancha_ns.doc(params={'fecha': {'description': 'Fecha en formato YYYY-MM-DD', 'required': True, 'example': '2024-12-25'}})
    @cancha_ns.response(200, 'Horarios disponibles obtenidos', horarios_disponibles_model)
    @cancha_ns.response(400, 'Fecha requerida')
    @cancha_ns.response(500, 'Error al obtener horarios')
    def get(self, cancha_id):
        """Obtener horarios disponibles para una cancha en una fecha específica"""
        print(f"🎯 Llegó request a /cancha/{cancha_id}/horarios-disponibles GET")
        try:
            fecha = request.args.get('fecha')
            if not fecha:
                return {"message": "Debe enviar la fecha en formato YYYY-MM-DD"}, 400

            disponibles = CanchaService.obtener_horarios_disponibles(cancha_id, fecha)
            return {"horarios_disponibles": disponibles}, 200
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"message": "Error al obtener horarios"}, 500