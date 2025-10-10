from flask import request
from flask_restx import Namespace, Resource, fields
from app.services.cancha_service import CanchaService

cancha_ns = Namespace('cancha', description='Operaciones con canchas')

# Modelo de entrada en Swagger
cancha_model = cancha_ns.model('Cancha', {
    'nombre': fields.String(required=True),
    'tipo': fields.String(required=True),
    'subtipo': fields.String(required=True),
    'direccion': fields.String(required=True),
    'latitud': fields.Float(required=True),
    'longitud': fields.Float(required=True),
    'direccion_completa': fields.String(required=True),
    'superficie': fields.String(required=True),
    'capacidad': fields.Integer(required=True),
    'precio_hora': fields.Float(required=True),
    'descripcion': fields.String(required=True),
    'estado': fields.String(enum=['activa', 'inactiva', 'en_mantenimiento']),
    'imagenes': fields.List(fields.String),
    'horarios': fields.List(fields.Nested(cancha_ns.model('Horario', {
        'dia_semana': fields.String(enum=['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']),
        'hora': fields.String
    }))),
    'reglas': fields.List(fields.Nested(cancha_ns.model('Regla', {
        'regla': fields.String,
    }))),
    'amenidades': fields.List(fields.Nested(cancha_ns.model('Amenidad', {
        'amenidad': fields.String,
    })))
})

# Ruta para CREAR cancha (POST)
@cancha_ns.route('/')
class CanchaCreateResource(Resource):
    @cancha_ns.expect(cancha_model)
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
    def get(self):
        """Obtener todas las canchas"""
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
    @cancha_ns.doc(params={'fecha': 'Formato YYYY-MM-DD'})
    def get(self, cancha_id):
        """Obtener horarios disponibles para una cancha"""
        print(f"🎯 Llegó request a /cancha/{cancha_id}/horarios-disponibles GET")
        try:
            fecha = request.args.get('fecha')
            if not fecha:
                return {"message": "Debe enviar la fecha"}, 400

            disponibles = CanchaService.obtener_horarios_disponibles(cancha_id, fecha)
            return {"horarios_disponibles": disponibles}, 200
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"message": "Error al obtener horarios"}, 500