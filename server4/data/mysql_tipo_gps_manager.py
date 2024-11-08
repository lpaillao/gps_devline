# Archivo: data/mysql_tipo_gps_manager.py
import logging
from .mysql_database import MySQLDatabase

class MySQLTipoGPSManager:
    def __init__(self):
        self.table_name = "tipos_gps"

    def get_all_tipos_gps(self):
        """
        Obtiene todos los tipos de GPS.
        """
        try:
            query = f"SELECT * FROM {self.table_name}"
            return MySQLDatabase.execute_query(query)
        except Exception as e:
            logging.exception(f"Error getting tipos GPS: {str(e)}")
            raise

    def create_tipo_gps(self, nombre):
        """
        Crea un nuevo tipo de GPS.
        """
        try:
            query = f"INSERT INTO {self.table_name} (nombre) VALUES (%s)"
            result = MySQLDatabase.execute_query(query, (nombre,))
            return result is not None
        except Exception as e:
            logging.exception(f"Error creating tipo GPS: {str(e)}")
            raise

    def update_tipo_gps(self, id, nombre):
        """
        Actualiza un tipo de GPS existente.
        """
        try:
            query = f"UPDATE {self.table_name} SET nombre = %s WHERE id = %s"
            result = MySQLDatabase.execute_query(query, (nombre, id))
            return result is not None
        except Exception as e:
            logging.exception(f"Error updating tipo GPS: {str(e)}")
            raise

    def delete_tipo_gps(self, id):
        """
        Elimina un tipo de GPS.
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = MySQLDatabase.execute_query(query, (id,))
            return result is not None
        except Exception as e:
            logging.exception(f"Error deleting tipo GPS: {str(e)}")
            raise

    def get_tipo_gps_by_id(self, id):
        """
        Obtiene un tipo de GPS por su ID.
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %s"
            result = MySQLDatabase.execute_query(query, (id,))
            return result[0] if result else None
        except Exception as e:
            logging.exception(f"Error getting tipo GPS by ID: {str(e)}")
            raise