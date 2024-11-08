# Archivo: data/mysql_asignacion_dispositivo_manager.py
import logging
from .mysql_database import MySQLDatabase

class MySQLAsignacionDispositivoManager:
    def __init__(self):
        self.table_name = "asignacion_dispositivos"

    def get_all_asignaciones(self):
        """
        Obtiene todas las asignaciones con información relacionada.
        """
        try:
            query = f"""
                SELECT a.*, d.imei, u.username as usuario, e.nombre as empresa 
                FROM {self.table_name} a
                LEFT JOIN dispositivos_gps d ON a.dispositivo_gps_id = d.id
                LEFT JOIN users u ON a.usuario_id = u.id
                LEFT JOIN empresas e ON a.empresa_id = e.id
            """
            return MySQLDatabase.execute_query(query)
        except Exception as e:
            logging.exception(f"Error getting asignaciones: {str(e)}")
            raise

    def create_asignacion(self, dispositivo_gps_id, usuario_id=None, empresa_id=None):
        """
        Crea una nueva asignación de dispositivo.
        """
        try:
            query = f"""
                INSERT INTO {self.table_name} 
                (dispositivo_gps_id, usuario_id, empresa_id) 
                VALUES (%s, %s, %s)
            """
            result = MySQLDatabase.execute_query(
                query, 
                (dispositivo_gps_id, usuario_id, empresa_id)
            )
            return result is not None
        except Exception as e:
            logging.exception(f"Error creating asignación: {str(e)}")
            raise

    def update_asignacion(self, id, dispositivo_gps_id, usuario_id=None, empresa_id=None):
        """
        Actualiza una asignación existente.
        """
        try:
            query = f"""
                UPDATE {self.table_name} 
                SET dispositivo_gps_id = %s, usuario_id = %s, empresa_id = %s 
                WHERE id = %s
            """
            result = MySQLDatabase.execute_query(
                query, 
                (dispositivo_gps_id, usuario_id, empresa_id, id)
            )
            return result is not None
        except Exception as e:
            logging.exception(f"Error updating asignación: {str(e)}")
            raise

    def delete_asignacion(self, id):
        """
        Elimina una asignación.
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = MySQLDatabase.execute_query(query, (id,))
            return result is not None
        except Exception as e:
            logging.exception(f"Error deleting asignación: {str(e)}")
            raise

    def get_asignaciones_por_usuario(self, usuario_id):
        """
        Obtiene todas las asignaciones de un usuario específico.
        """
        try:
            query = f"""
                SELECT a.*, d.imei, d.modelo, d.marca, t.nombre as tipo_gps
                FROM {self.table_name} a
                INNER JOIN dispositivos_gps d ON a.dispositivo_gps_id = d.id
                INNER JOIN tipos_gps t ON d.tipo_gps_id = t.id
                WHERE a.usuario_id = %s
            """
            return MySQLDatabase.execute_query(query, (usuario_id,))
        except Exception as e:
            logging.exception(f"Error getting asignaciones por usuario: {str(e)}")
            raise

    def get_asignaciones_por_empresa(self, empresa_id):
        """
        Obtiene todas las asignaciones de una empresa específica.
        """
        try:
            query = f"""
                SELECT a.*, d.imei, d.modelo, d.marca, t.nombre as tipo_gps, 
                       u.username as usuario
                FROM {self.table_name} a
                INNER JOIN dispositivos_gps d ON a.dispositivo_gps_id = d.id
                INNER JOIN tipos_gps t ON d.tipo_gps_id = t.id
                LEFT JOIN users u ON a.usuario_id = u.id
                WHERE a.empresa_id = %s
            """
            return MySQLDatabase.execute_query(query, (empresa_id,))
        except Exception as e:
            logging.exception(f"Error getting asignaciones por empresa: {str(e)}")
            raise

    def get_asignacion_por_dispositivo(self, dispositivo_gps_id):
        """
        Obtiene la asignación de un dispositivo específico.
        """
        try:
            query = f"""
                SELECT a.*, u.username as usuario, e.nombre as empresa
                FROM {self.table_name} a
                LEFT JOIN users u ON a.usuario_id = u.id
                LEFT JOIN empresas e ON a.empresa_id = e.id
                WHERE a.dispositivo_gps_id = %s
            """
            result = MySQLDatabase.execute_query(query, (dispositivo_gps_id,))
            return result[0] if result else None
        except Exception as e:
            logging.exception(f"Error getting asignación por dispositivo: {str(e)}")
            raise
