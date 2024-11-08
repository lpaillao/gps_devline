# Archivo: data/mysql_empresa_manager.py
import logging
from .mysql_database import MySQLDatabase

class MySQLEmpresaManager:
    def __init__(self):
        self.table_name = "empresas"

    def get_all_empresas(self):
        """
        Obtiene todas las empresas.
        """
        try:
            query = f"SELECT * FROM {self.table_name}"
            return MySQLDatabase.execute_query(query)
        except Exception as e:
            logging.exception(f"Error getting empresas: {str(e)}")
            raise

    def create_empresa(self, nombre, direccion, telefono, email):
        """
        Crea una nueva empresa.
        """
        try:
            query = f"""
                INSERT INTO {self.table_name} 
                (nombre, direccion, telefono, email) 
                VALUES (%s, %s, %s, %s)
            """
            result = MySQLDatabase.execute_query(
                query, 
                (nombre, direccion, telefono, email)
            )
            return result is not None
        except Exception as e:
            logging.exception(f"Error creating empresa: {str(e)}")
            raise

    def update_empresa(self, id, nombre, direccion, telefono, email):
        """
        Actualiza una empresa existente.
        """
        try:
            query = f"""
                UPDATE {self.table_name} 
                SET nombre = %s, direccion = %s, telefono = %s, email = %s 
                WHERE id = %s
            """
            result = MySQLDatabase.execute_query(
                query, 
                (nombre, direccion, telefono, email, id)
            )
            return result is not None
        except Exception as e:
            logging.exception(f"Error updating empresa: {str(e)}")
            raise

    def delete_empresa(self, id):
        """
        Elimina una empresa.
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = MySQLDatabase.execute_query(query, (id,))
            return result is not None
        except Exception as e:
            logging.exception(f"Error deleting empresa: {str(e)}")
            raise

    def get_empresa_by_id(self, id):
        """
        Obtiene una empresa por su ID.
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %s"
            result = MySQLDatabase.execute_query(query, (id,))
            return result[0] if result else None
        except Exception as e:
            logging.exception(f"Error getting empresa by ID: {str(e)}")
            raise