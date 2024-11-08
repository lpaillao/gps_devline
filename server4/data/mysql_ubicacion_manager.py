# Archivo: data/mysql_ubicacion_manager.py
import logging
from .mysql_database import MySQLDatabase

class MySQLUbicacionManager:
    def __init__(self):
        self.table_name = "ubicaciones"

    def get_all_ubicaciones(self):
        """
        Obtiene todas las ubicaciones ordenadas por fecha/hora descendente.
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                ORDER BY fecha_hora DESC
            """
            return MySQLDatabase.execute_query(query)
        except Exception as e:
            logging.exception(f"Error getting ubicaciones: {str(e)}")
            raise

    def create_ubicacion(self, dispositivo_gps_id, latitud, longitud, fecha_hora, velocidad=None, bateria=None):
        """
        Crea un nuevo registro de ubicación.
        """
        try:
            query = f"""
                INSERT INTO {self.table_name} 
                (dispositivo_gps_id, latitud, longitud, fecha_hora, velocidad, bateria) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            result = MySQLDatabase.execute_query(
                query, 
                (dispositivo_gps_id, latitud, longitud, fecha_hora, velocidad, bateria)
            )
            return result is not None
        except Exception as e:
            logging.exception(f"Error creating ubicacion: {str(e)}")
            raise

    def get_ubicaciones_por_dispositivo(self, dispositivo_gps_id):
        """
        Obtiene todas las ubicaciones de un dispositivo específico.
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE dispositivo_gps_id = %s 
                ORDER BY fecha_hora DESC
            """
            return MySQLDatabase.execute_query(query, (dispositivo_gps_id,))
        except Exception as e:
            logging.exception(f"Error getting ubicaciones por dispositivo: {str(e)}")
            raise

    def get_ultima_ubicacion_por_dispositivo(self, dispositivo_gps_id):
        """
        Obtiene la última ubicación registrada de un dispositivo.
        """
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE dispositivo_gps_id = %s 
                ORDER BY fecha_hora DESC 
                LIMIT 1
            """
            result = MySQLDatabase.execute_query(query, (dispositivo_gps_id,))
            return result[0] if result else None
        except Exception as e:
            logging.exception(f"Error getting última ubicación: {str(e)}")
            raise