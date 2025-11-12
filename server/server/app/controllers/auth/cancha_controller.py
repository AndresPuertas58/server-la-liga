from flask import request
from flask_restx import Resource, fields
from app.services.auth.cancha_service import CanchaService
import json
from flask import request, send_file, abort, make_response, current_app, send_from_directory
import os
from urllib.parse import quote

# Importar namespace y modelos
from . import cancha_ns, cancha_model, cancha_response_model, horarios_disponibles_model, cancha_creada_response_model, cancha_error_model

# Ruta para CREAR cancha (POST) - ACTUALIZADO para multipart/form-data
@cancha_ns.route('/create')
class CanchaCreateResource(Resource):
    @cancha_ns.doc(description='''Crear una nueva cancha con soporte para subida de imágenes.''')
    @cancha_ns.response(201, 'Cancha creada correctamente', cancha_creada_response_model)
    @cancha_ns.response(400, 'Error de validación', cancha_error_model)
    @cancha_ns.response(401, 'No autorizado', cancha_error_model)
    @cancha_ns.response(500, 'Error interno del servidor', cancha_error_model)
    def post(self):
        """Crear una nueva cancha con soporte para subida de imágenes"""
        print("🎯 Llegó request a /cancha/create POST")
        print(f"📋 Content-Type: {request.content_type}")
        
        try:
            # ✅ SOPORTAR multipart/form-data
            if request.content_type and 'multipart/form-data' in request.content_type:
                print("📦 Datos recibidos como multipart/form-data")
                
                # Obtener datos del form
                data = {
                    'nombre': request.form.get('nombre'),
                    'tipo': request.form.get('tipo'),
                    'subtipo': request.form.get('subtipo'),
                    'direccion': request.form.get('direccion'),
                    'latitud': request.form.get('latitud'),
                    'longitud': request.form.get('longitud'),
                    'direccion_completa': request.form.get('direccion_completa'),
                    'superficie': request.form.get('superficie'),
                    'capacidad': request.form.get('capacidad'),
                    'precio_hora': request.form.get('precio_hora'),
                    'descripcion': request.form.get('descripcion'),
                    'estado': request.form.get('estado', 'activa')
                }
                
                print(f"📥 Datos recibidos del form: {data}")
                
                # ✅ DEBUG: Mostrar todos los campos recibidos
                print("🔍 Campos en request.form:")
                for key in request.form.keys():
                    print(f"  {key}: {request.form.get(key)}")
                
                print("🔍 Archivos en request.files:")
                for key in request.files.keys():
                    files = request.files.getlist(key)
                    print(f"  {key}: {len(files)} archivos")
                    for i, file in enumerate(files):
                        print(f"    [{i}] {file.filename} ({file.content_type})")
                
                # Procesar listas desde JSON strings
                try:
                    data['horarios'] = json.loads(request.form.get('horarios', '[]'))
                    data['reglas'] = json.loads(request.form.get('reglas', '[]'))
                    data['amenidades'] = json.loads(request.form.get('amenidades', '[]'))
                    data['imagenes'] = json.loads(request.form.get('imagenes', '[]'))
                except json.JSONDecodeError as e:
                    print(f"❌ Error decodificando JSON: {str(e)}")
                    return {
                        "error": "Error al procesar datos JSON en formulario",
                        "codigo": "JSON_INVALIDO",
                        "detalles": str(e)
                    }, 400
                
                # ✅ Obtener archivos de imágenes - MÚLTIPLES FORMATOS SOPORTADOS
                imagenes_files = []
                
                # Formato 1: 'imagenes[]' (array)
                if 'imagenes[]' in request.files:
                    imagenes_files = request.files.getlist('imagenes[]')
                    print(f"📸 Archivos recibidos como 'imagenes[]': {len(imagenes_files)}")
                
                # Formato 2: 'imagenes' (individual)
                elif 'imagenes' in request.files:
                    imagenes_files = [request.files['imagenes']]
                    print(f"📸 Archivo recibido como 'imagenes': {len(imagenes_files)}")
                
                # Formato 3: 'imagenes[0]', 'imagenes[1]', etc.
                else:
                    # Buscar archivos con patrón imagenes[0], imagenes[1], etc.
                    i = 0
                    while f'imagenes[{i}]' in request.files:
                        file = request.files[f'imagenes[{i}]']
                        if file and file.filename:  # Verificar que sea un archivo válido
                            imagenes_files.append(file)
                        i += 1
                    
                    if imagenes_files:
                        print(f"📸 Archivos recibidos como 'imagenes[0]...': {len(imagenes_files)}")
                
                print(f"📦 Total de archivos de imagen a procesar: {len(imagenes_files)}")
                
                # Validar datos requeridos
                campos_requeridos = ['nombre', 'tipo', 'subtipo', 'direccion', 'latitud', 'longitud', 
                                   'direccion_completa', 'superficie', 'capacidad', 'precio_hora', 'descripcion']
                
                campos_faltantes = [campo for campo in campos_requeridos if not data.get(campo)]
                if campos_faltantes:
                    return {
                        "error": f"Campos requeridos faltantes: {', '.join(campos_faltantes)}",
                        "codigo": "CAMPOS_REQUERIDOS_FALTANTES"
                    }, 400
                
                # Convertir tipos de datos
                try:
                    data['latitud'] = float(data['latitud']) if data['latitud'] else None
                    data['longitud'] = float(data['longitud']) if data['longitud'] else None
                    data['capacidad'] = int(data['capacidad'])
                    data['precio_hora'] = float(data['precio_hora'])
                except (ValueError, TypeError) as e:
                    return {
                        "error": "Error en tipos de datos: latitud, longitud, capacidad y precio_hora deben ser números",
                        "codigo": "TIPO_DATO_INVALIDO",
                        "detalles": str(e)
                    }, 400
                
                # Crear cancha con archivos de imagen
                print("🔄 Llamando a servicio para crear cancha...")
                cancha = CanchaService.crear_cancha_con_todo(data, imagenes_files)
                
            else:
                # Formato JSON tradicional
                print("📦 Datos recibidos como JSON")
                data = request.json
                print(f"📥 Datos recibidos: {list(data.keys())}")
                
                # Validar datos requeridos
                campos_requeridos = ['nombre', 'tipo', 'subtipo', 'direccion', 'latitud', 'longitud', 
                                   'direccion_completa', 'superficie', 'capacidad', 'precio_hora', 'descripcion']
                
                campos_faltantes = [campo for campo in campos_requeridos if campo not in data]
                if campos_faltantes:
                    return {
                        "error": f"Campos requeridos faltantes: {', '.join(campos_faltantes)}",
                        "codigo": "CAMPOS_REQUERIDOS_FALTANTES"
                    }, 400
                
                cancha = CanchaService.crear_cancha_con_todo(data)
            
            return {
                'message': 'Cancha creada correctamente',
                'cancha': cancha.to_dict_completo()
            }, 201
            
        except PermissionError as e:
            print(f"❌ Error de permisos: {str(e)}")
            return {"error": str(e), "codigo": "NO_AUTORIZADO"}, 401
        except ValueError as e:
            print(f"❌ Error de validación: {str(e)}")
            return {"error": str(e), "codigo": "VALIDACION_FALLIDA"}, 400
        except Exception as e:
            print(f"❌ Error interno: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": "Error interno del servidor", "codigo": "ERROR_INTERNO"}, 500

@cancha_ns.route('/list')
class CanchaListResource(Resource):
    def get(self):
        """Obtener todas las canchas activas con URLs de imágenes WebP"""
        print("🎯 Llegó request a /cancha/list GET")
        try:
            # ✅ El servicio retorna diccionarios con URLs WebP
            canchas = CanchaService.obtener_todas_las_canchas()
            
            print(f"✅ Retornando {len(canchas)} canchas con URLs WebP")
            return {
                'success': True,
                'data': canchas,
                'count': len(canchas),
                'formato_imagenes': 'webp_url'
            }, 200
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {
                "success": False,
                "error": "Error al obtener canchas", 
                "codigo": "ERROR_OBTENER_CANCHAS"
            }, 500

@cancha_ns.route('/<int:cancha_id>/imagen-webp/<filename>')
class CanchaImagenWebPResource(Resource):
    def get(self, cancha_id, filename):
        """Servir archivo WebP de cancha"""
        try:
            # Construir ruta al directorio WebP
            webp_folder = os.path.join(
                current_app.root_path, 
                'utils', 'pictures', 'canchas', 
                str(cancha_id), 'webp'
            )
            
            # Verificar que el archivo existe
            file_path = os.path.join(webp_folder, filename)
            if not os.path.exists(file_path):
                print(f"❌ Archivo WebP no encontrado: {file_path}")
                return {"error": "Imagen WebP no encontrada"}, 404
            
            print(f"📤 Sirviendo archivo WebP: {filename}")
            return send_from_directory(webp_folder, filename)
            
        except Exception as e:
            print(f"❌ Error sirviendo imagen WebP: {str(e)}")
            return {"error": "Error al cargar imagen WebP"}, 500

@cancha_ns.route('/<int:id>')
class CanchaDetailResource(Resource):
    def get(self, id):
        """Obtener cancha por ID con URLs de imágenes WebP"""
        print(f"🎯 Llegó request a /cancha/{id} GET")
        try:
            cancha = CanchaService.obtener_cancha_por_id(id)
            if not cancha:
                return {
                    "success": False,
                    "error": "Cancha no encontrada", 
                    "codigo": "CANCHA_NO_ENCONTRADA"
                }, 404
            
            # Convertir a diccionario con URLs WebP
            cancha_data = {
                'id': cancha.id,
                'nombre': cancha.nombre,
                'tipo': cancha.tipo,
                'subtipo': cancha.subtipo,
                'direccion': cancha.direccion,
                'latitud': cancha.latitud,
                'longitud': cancha.longitud,
                'direccion_completa': cancha.direccion_completa,
                'superficie': cancha.superficie,
                'capacidad': cancha.capacidad,
                'precio_hora': float(cancha.precio_hora) if cancha.precio_hora else None,
                'descripcion': cancha.descripcion,
                'estado': cancha.estado,
                'imagenes_webp': []
            }
            
            for img in cancha.imagenes:
                if img.url_imagen.startswith('/utils/pictures/'):
                    cancha_data['imagenes_webp'].append({
                        'id': img.id,
                        'orden': img.orden,
                        'url_webp': f"/cancha/{cancha.id}/imagen-webp/{os.path.basename(img.url_imagen)}",
                        'nombre': os.path.basename(img.url_imagen),
                        'formato': 'webp'
                    })
                else:
                    cancha_data['imagenes_webp'].append({
                        'id': img.id,
                        'orden': img.orden,
                        'url': img.url_imagen,
                        'formato': 'externo'
                    })
            
            return {
                'success': True,
                'data': cancha_data
            }, 200
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {
                "success": False,
                "error": "Error al obtener cancha", 
                "codigo": "ERROR_OBTENER_CANCHA"
            }, 500

# Ruta para horarios disponibles
@cancha_ns.route('/<int:cancha_id>/horarios-disponibles')
class HorariosDisponiblesResource(Resource):
    @cancha_ns.doc(params={'fecha': {'description': 'Fecha en formato YYYY-MM-DD', 'required': True, 'example': '2024-12-25'}})
    @cancha_ns.response(200, 'Horarios disponibles obtenidos', horarios_disponibles_model)
    @cancha_ns.response(400, 'Fecha requerida', cancha_error_model)
    @cancha_ns.response(500, 'Error al obtener horarios', cancha_error_model)
    def get(self, cancha_id):
        """Obtener horarios disponibles para una cancha en una fecha específica"""
        print(f"🎯 Llegó request a /cancha/{cancha_id}/horarios-disponibles GET")
        try:
            fecha = request.args.get('fecha')
            if not fecha:
                return {"error": "Debe enviar la fecha en formato YYYY-MM-DD", "codigo": "FECHA_REQUERIDA"}, 400

            disponibles = CanchaService.obtener_horarios_disponibles(cancha_id, fecha)
            return {
                "horarios_disponibles": disponibles,
                "fecha": fecha,
                "cancha_id": cancha_id,
                "total_disponibles": len(disponibles)
            }, 200
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"error": "Error al obtener horarios", "codigo": "ERROR_OBTENER_HORARIOS"}, 500