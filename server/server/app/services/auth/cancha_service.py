import os
import uuid
import json
from PIL import Image
from flask import current_app, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, time, timedelta
from app.models.cancha import Cancha
from app.models.imagen import Imagen
from app.models.horario_cancha import HorarioCancha
from app.models.regla_cancha import ReglaCancha
from app.models.amenidad_cancha import AmenidadCancha
from app.utils.database import db
from app.utils.auth_utils import obtener_usuario_desde_token
from app.models.dia_festivo import DiaFestivo
from app.models.reserva import Reserva
from sqlalchemy import Numeric
import calendar

class CanchaService:

    @staticmethod
    def crear_cancha_con_todo(data, imagenes_files=None):
        print("🔍 Iniciando creación de cancha en servicio...")
        
        usuario, error, status = obtener_usuario_desde_token()
        if error:
            raise PermissionError("Usuario no autenticado")
        
        print(f"✅ Usuario autenticado: {usuario.email}")

        # Crear cancha
        cancha = Cancha(
            nombre=data['nombre'],
            tipo=data['tipo'],
            subtipo=data['subtipo'],
            direccion=data['direccion'],
            latitud=data['latitud'],
            longitud=data['longitud'],
            direccion_completa=data['direccion_completa'],
            superficie=data['superficie'],
            capacidad=data['capacidad'],
            precio_hora=data['precio_hora'],
            descripcion=data['descripcion'],
            estado=data.get('estado', 'activa')
        )

        db.session.add(cancha)
        db.session.flush()

        # ✅ MANEJO DE IMÁGENES - Guardar como WebP
        urls_imagenes = []
        if imagenes_files:
            for i, imagen_file in enumerate(imagenes_files):
                if imagen_file and imagen_file.filename:
                    url_imagen = CanchaService._guardar_y_convertir_a_webp(imagen_file, cancha.id)
                    if url_imagen:
                        urls_imagenes.append(url_imagen)
                        imagen = Imagen(cancha_id=cancha.id, url_imagen=url_imagen, orden=i)
                        db.session.add(imagen)
                        print(f"📸 Imagen convertida a WebP: {url_imagen}")

        # URLs de imágenes (compatibilidad)
        for i, url in enumerate(data.get('imagenes', [])):
            if url and url not in urls_imagenes:
                imagen = Imagen(cancha_id=cancha.id, url_imagen=url, orden=len(urls_imagenes) + i)
                db.session.add(imagen)

        # Horarios, reglas y amenidades
        CanchaService._procesar_horarios(data.get('horarios', []), cancha.id)
        CanchaService._procesar_reglas(data.get('reglas', []), cancha.id)
        CanchaService._procesar_amenidades(data.get('amenidades', []), cancha.id)

        db.session.commit()
        print("✅ Cancha creada exitosamente")
        return cancha

    @staticmethod
    def _guardar_y_convertir_a_webp(imagen_file, cancha_id):
        """
        Guardar imagen y convertir a WebP como archivo
        """
        try:
            # Crear directorios
            upload_folder = os.path.join(current_app.root_path, 'utils', 'pictures', 'canchas', str(cancha_id))
            webp_folder = os.path.join(upload_folder, 'webp')
            os.makedirs(webp_folder, exist_ok=True)
            
            # Generar nombres únicos
            original_filename = secure_filename(imagen_file.filename)
            name_without_ext = os.path.splitext(original_filename)[0]
            unique_id = uuid.uuid4().hex
            
            # Guardar original temporalmente
            temp_path = os.path.join(upload_folder, f"temp_{unique_id}_{original_filename}")
            imagen_file.save(temp_path)
            
            try:
                # Abrir y procesar imagen
                with Image.open(temp_path) as img:
                    # Convertir a RGB si es necesario
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    # Redimensionar si es muy grande (máximo 1200px en el lado más largo)
                    max_size = (1200, 1200)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Guardar como WebP
                    webp_filename = f"{unique_id}_{name_without_ext}.webp"
                    webp_path = os.path.join(webp_folder, webp_filename)
                    
                    # Guardar con calidad optimizada
                    img.save(webp_path, 'WEBP', quality=80, optimize=True)
                    
                    # Retornar ruta relativa del WebP para guardar en BD
                    relative_path = f"/utils/pictures/canchas/{cancha_id}/webp/{webp_filename}"
                    print(f"🖼️ Imagen convertida a WebP: {original_filename} -> {webp_filename}")
                    
                    return relative_path
                    
            finally:
                # Eliminar archivo temporal
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
        except Exception as e:
            print(f"❌ Error al procesar imagen: {str(e)}")
            return None

    @staticmethod
    def _procesar_horarios(horarios, cancha_id):
        """Procesar horarios de la cancha"""
        for horario in horarios:
            if 'hora_inicio' in horario and 'hora_fin' in horario:
                h = HorarioCancha(
                    cancha_id=cancha_id,
                    dia_semana=horario['dia_semana'],
                    hora_inicio=datetime.strptime(horario['hora_inicio'], '%H:%M').time(),
                    hora_fin=datetime.strptime(horario['hora_fin'], '%H:%M').time(),
                    intervalo_minutos=horario.get('intervalo_minutos', 60),
                    disponible=horario.get('disponible', True)
                )
                db.session.add(h)

    @staticmethod
    def _procesar_reglas(reglas, cancha_id):
        """Procesar reglas de la cancha"""
        for regla in reglas:
            r = ReglaCancha(cancha_id=cancha_id, regla=regla['regla'])
            db.session.add(r)

    @staticmethod
    def _procesar_amenidades(amenidades, cancha_id):
        """Procesar amenidades de la cancha"""
        for amenidad in amenidades:
            a = AmenidadCancha(cancha_id=cancha_id, amenidad=amenidad['amenidad'])
            db.session.add(a)

    @staticmethod
    def obtener_todas_las_canchas():
        """Obtener todas las canchas con URLs de imágenes WebP y horarios"""
        print("🔍 Obteniendo todas las canchas activas")
        canchas = Cancha.query.filter_by(estado='activa').all()
        print(f"✅ Encontradas {len(canchas)} canchas activas")
        
        canchas_dict = []
        for cancha in canchas:
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
                'imagenes_webp': [],  # ✅ URLs de archivos WebP
                'horarios': [],       # ✅ Horarios de la cancha
                'reglas': [],         # ✅ Reglas de la cancha
                'amenidades': []      # ✅ Amenidades de la cancha
            }
            
            # Procesar imágenes como URLs WebP
            for img in cancha.imagenes:
                if img.url_imagen.startswith('/utils/pictures/'):
                    # Es una imagen local WebP
                    cancha_data['imagenes_webp'].append({
                        'id': img.id,
                        'orden': img.orden,
                        'url_webp': CanchaService._construir_url_accesible(img.url_imagen, cancha.id),
                        'nombre': os.path.basename(img.url_imagen),
                        'formato': 'webp'
                    })
                else:
                    # Es una URL externa
                    cancha_data['imagenes_webp'].append({
                        'id': img.id,
                        'orden': img.orden,
                        'url': img.url_imagen,
                        'formato': 'externo'
                    })
            
            # ✅ Procesar horarios
            for horario in cancha.horarios:
                cancha_data['horarios'].append({
                    'id': horario.id,
                    'dia_semana': horario.dia_semana,
                    'hora_inicio': horario.hora_inicio.strftime('%H:%M') if horario.hora_inicio else None,
                    'hora_fin': horario.hora_fin.strftime('%H:%M') if horario.hora_fin else None,
                    'intervalo_minutos': horario.intervalo_minutos,
                    'disponible': horario.disponible
                })
            
            # ✅ Procesar reglas
            for regla in cancha.reglas:
                cancha_data['reglas'].append({
                    'id': regla.id,
                    'regla': regla.regla
                })
            
            # ✅ Procesar amenidades
            for amenidad in cancha.amenidades:
                cancha_data['amenidades'].append({
                    'id': amenidad.id,
                    'amenidad': amenidad.amenidad
                })
            
            canchas_dict.append(cancha_data)
        
        return canchas_dict

    @staticmethod
    def _construir_url_accesible(ruta_imagen, cancha_id):
        """
        Construir URL accesible para archivo WebP
        """
        filename = os.path.basename(ruta_imagen)
        return f"/cancha/{cancha_id}/imagen-webp/{filename}"

    @staticmethod
    def obtener_cancha_por_id(cancha_id):
        print(f"🔍 Buscando cancha ID: {cancha_id}")
        cancha = Cancha.query.get(cancha_id)
        if cancha:
            print(f"✅ Cancha encontrada: {cancha.nombre}")
        else:
            print("❌ Cancha no encontrada")
        return cancha
    
    @staticmethod
    def obtener_horarios_disponibles(cancha_id: int, fecha_str: str):
        print(f"🔍 Obteniendo horarios disponibles para cancha {cancha_id} en fecha {fecha_str}")
        
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

        # Verificar si es festivo
        festivo = DiaFestivo.query.filter_by(fecha=fecha).first()
        if festivo:
            tipo_dia = 'domingo'  # O el tipo que uses para festivos
            print(f"🎉 Fecha {fecha_str} es festivo, se usa tipo: {tipo_dia}")
        else:
            dias_map = {
                'monday': 'lunes',
                'tuesday': 'martes',
                'wednesday': 'miercoles',
                'thursday': 'jueves',
                'friday': 'viernes',
                'saturday': 'sabado',
                'sunday': 'domingo'
            }  
            dia_semana = calendar.day_name[fecha.weekday()].lower()
            tipo_dia = dias_map.get(dia_semana)
            print(f"📅 Fecha {fecha_str} es {tipo_dia}")

        # Obtener horarios de ese día para la cancha (NUEVO: rangos)
        horarios_rango = HorarioCancha.query.filter_by(
            cancha_id=cancha_id, 
            dia_semana=tipo_dia,
            disponible=True
        ).all()

        # Generar todos los horarios disponibles desde los rangos
        todos_horarios_disponibles = set()
        for horario_rango in horarios_rango:
            horarios_generados = CanchaService._generar_horarios_desde_rango(
                horario_rango.hora_inicio, 
                horario_rango.hora_fin, 
                horario_rango.intervalo_minutos
            )
            todos_horarios_disponibles.update(horarios_generados)
        
        print(f"🕒 Horarios configurados: {sorted(todos_horarios_disponibles)}")

        # Obtener reservas ya hechas para esa cancha en esa fecha
        reservas = Reserva.query.filter_by(cancha_id=cancha_id, fecha=fecha).all()
        horas_reservadas = {r.hora.strftime('%H:%M') for r in reservas}
        print(f"🔒 Horarios reservados: {sorted(horas_reservadas)}")

        # Calcular horarios disponibles
        disponibles = sorted(todos_horarios_disponibles - horas_reservadas)
        print(f"✅ Horarios disponibles: {disponibles}")

        return disponibles

    @staticmethod
    def _generar_horarios_desde_rango(hora_inicio: time, hora_fin: time, intervalo_minutos: int):
        """
        Generar lista de horarios basado en un rango y intervalo
        """
        horarios = []
        current_time = datetime.combine(datetime.today(), hora_inicio)
        end_time = datetime.combine(datetime.today(), hora_fin)

        while current_time < end_time:
            horarios.append(current_time.time().strftime('%H:%M'))
            current_time += timedelta(minutes=intervalo_minutos)

        return horarios

    @staticmethod
    def verificar_disponibilidad_horario(cancha_id: int, dia_semana: str, hora_solicitada: str):
        """
        Verificar si un horario específico está disponible según los rangos configurados
        """
        hora_time = datetime.strptime(hora_solicitada, '%H:%M').time()
        
        horarios_disponibles = HorarioCancha.query.filter_by(
            cancha_id=cancha_id,
            dia_semana=dia_semana,
            disponible=True
        ).all()

        for horario in horarios_disponibles:
            if CanchaService._hora_en_rango(hora_time, horario.hora_inicio, horario.hora_fin, horario.intervalo_minutos):
                return True
        
        return False

    @staticmethod
    def _hora_en_rango(hora_solicitada: time, hora_inicio: time, hora_fin: time, intervalo_minutos: int):
        """
        Verificar si una hora específica está dentro de un rango considerando el intervalo
        """
        hora_solicitada_dt = datetime.combine(datetime.today(), hora_solicitada)
        inicio_dt = datetime.combine(datetime.today(), hora_inicio)
        fin_dt = datetime.combine(datetime.today(), hora_fin)

        # Verificar que esté dentro del rango general
        if not (inicio_dt <= hora_solicitada_dt < fin_dt):
            return False

        # Verificar que coincida con el intervalo
        tiempo_desde_inicio = hora_solicitada_dt - inicio_dt
        minutos_desde_inicio = tiempo_desde_inicio.total_seconds() / 60
        
        return minutos_desde_inicio % intervalo_minutos == 0
    
    