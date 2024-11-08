# Archivo: data/mysql_dispositivo_gps_manager.py
import logging
from .mysql_database import MySQLDatabase

class MySQLDispositivoGPSManager:
    def __init__(self):
        self.table_name = "dispositivos_gps"

    def get_all_dispositivos_gps(self):
        try:
            query = f"""
                SELECT d.*, t.nombre as tipo_gps 
                FROM {self.table_name} d
                INNER JOIN tipos_gps t ON d.tipo_gps_id = t.id
            """
            return MySQLDatabase.execute_query(query)
        except Exception as e:
            logging.exception(f"Error getting dispositivos GPS: {str(e)}")
            raise

    def create_dispositivo_gps(self, imei, modelo, marca, tipo_gps_id):
        try:
            query = f"""
                INSERT INTO {self.table_name} 
                (imei, modelo, marca, tipo_gps_id) 
                VALUES (%s, %s, %s, %s)
            """
            result = MySQLDatabase.execute_query(
                query, 
                (imei, modelo, marca, tipo_gps_id)
            )
            return result is not None
        except Exception as e:
            logging.exception(f"Error creating dispositivo GPS: {str(e)}")
            raise

    def update_dispositivo_gps(self, id, imei, modelo, marca, tipo_gps_id):
        try:
            query = f"""
                UPDATE {self.table_name} 
                SET imei = %s, modelo = %s, marca = %s, tipo_gps_id = %s 
                WHERE id = %s
            """
            result = MySQLDatabase.execute_query(
                query, 
                (imei, modelo, marca, tipo_gps_id, id)
            )
            return result is not None
        except Exception as e:
            logging.exception(f"Error updating dispositivo GPS: {str(e)}")
            raise

    def delete_dispositivo_gps(self, id):
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = MySQLDatabase.execute_query(query, (id,))
            return result is not None
        except Exception as e:
            logging.exception(f"Error deleting dispositivo GPS: {str(e)}")
            raise