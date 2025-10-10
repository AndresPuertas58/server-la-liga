# app/services/player_reserva_service.py
from app.models.reserva import Reserva
from app.models.cancha import Cancha
from app.utils.database import db
from datetime import datetime

class PlayerReservaService:
    @staticmethod
    def obtener_reservas_jugador(user_id: int) -> dict:
        """
        Obtener todas las reservas de un jugador
        """
        try:
            print(f"🔍 Buscando reservas para el jugador ID: {user_id}")
            
            # Obtener todas las reservas del usuario ordenadas por fecha y hora
            reservas = Reserva.query.filter_by(user_id=user_id).order_by(
                Reserva.fecha.desc(), 
                Reserva.hora.desc()
            ).all()
            
            print(f"✅ Encontradas {len(reservas)} reservas")
            
            # Formatear la respuesta
            reservas_data = []
            for reserva in reservas:
                # Obtener información de la cancha
                cancha_nombre = "Cancha no disponible"
                cancha_direccion = ""
                precio = 0.0
                
                if reserva.cancha:
                    cancha_nombre = reserva.cancha.nombre
                    cancha_direccion = reserva.cancha.direccion
                    # Usar el precio de la cancha si está disponible
                    precio = float(reserva.cancha.precio) if hasattr(reserva.cancha, 'precio') and reserva.cancha.precio else 0.0
                
                # Formatear fecha
                if hasattr(reserva.fecha, 'isoformat'):
                    fecha_formateada = reserva.fecha.isoformat()
                else:
                    fecha_formateada = str(reserva.fecha)
                
                # Formatear fecha de creación
                creado_en = None
                if hasattr(reserva, 'creado_en') and reserva.creado_en and hasattr(reserva.creado_en, 'isoformat'):
                    creado_en = reserva.creado_en.isoformat()
                
                # Construir el objeto de reserva
                reserva_obj = {
                    "id": reserva.id,
                    "cancha_id": reserva.cancha_id,
                    "cancha_nombre": cancha_nombre,
                    "cancha_direccion": cancha_direccion,
                    "fecha": fecha_formateada,
                    "hora": str(reserva.hora),
                    "estado": reserva.estado if hasattr(reserva, 'estado') else "confirmada",
                    "precio": precio,
                    "creado_en": creado_en
                }
                
                # Agregar campos adicionales si existen en el modelo
                if hasattr(reserva, 'duracion'):
                    reserva_obj["duracion"] = reserva.duracion
                if hasattr(reserva, 'metodo_pago'):
                    reserva_obj["metodo_pago"] = reserva.metodo_pago
                
                reservas_data.append(reserva_obj)
            
            return {"reservas": reservas_data}
            
        except Exception as e:
            print(f"❌ Error al obtener reservas del jugador: {str(e)}")
            raise e

    @staticmethod
    def cancelar_reserva_jugador(user_id: int, reserva_id: int) -> dict:
        """
        Cancelar una reserva específica de un jugador
        """
        try:
            print(f"🔍 Buscando reserva {reserva_id} del jugador ID: {user_id}")
            
            # Buscar la reserva que pertenece a este usuario
            reserva = Reserva.query.filter_by(id=reserva_id, user_id=user_id).first()
            
            if not reserva:
                print("❌ Reserva no encontrada o no pertenece al usuario")
                raise ValueError("Reserva no encontrada")
            
            print("✅ Reserva encontrada, verificando condiciones de cancelación...")
            
            # Verificar si la reserva puede ser cancelada
            fecha_reserva = reserva.fecha
            hora_reserva = reserva.hora
            ahora = datetime.now()
            
            # Combinar fecha y hora de la reserva
            if isinstance(fecha_reserva, str):
                fecha_reserva = datetime.strptime(fecha_reserva, '%Y-%m-%d').date()
            
            datetime_reserva = datetime.combine(fecha_reserva, hora_reserva)
            
            # No permitir cancelar si ya pasó la reserva
            if datetime_reserva < ahora:
                print("❌ No se puede cancelar una reserva pasada")
                raise ValueError("No puedes cancelar una reserva pasada")
            
            # No permitir cancelar si falta poco tiempo
            tiempo_restante = datetime_reserva - ahora
            if tiempo_restante.total_seconds() < 3600:  # 1 hora antes
                print("❌ No se puede cancelar con menos de 1 hora de anticipación")
                raise ValueError("Solo puedes cancelar con al menos 1 hora de anticipación")
            
            # Proceder con la cancelación
            print("🗑️ Eliminando reserva...")
            db.session.delete(reserva)
            db.session.commit()
            
            print("✅ Reserva cancelada exitosamente")
            return {"message": "Reserva cancelada correctamente"}
            
        except ValueError as ve:
            print(f"❌ Error de validación: {str(ve)}")
            raise ve
        except Exception as e:
            print(f"❌ Error inesperado al cancelar reserva: {str(e)}")
            db.session.rollback()
            raise Exception(f"Error al cancelar la reserva: {str(e)}")