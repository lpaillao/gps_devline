import mysql.connector
from mysql.connector import Error
import logging
from config.config import Config
from typing import Optional, List, Dict, Any
import threading

class MySQLDatabase:
    """Clase para manejar la conexión y operaciones con MySQL"""
    
    _local = threading.local()
    _lock = threading.Lock()

    @classmethod
    def get_connection(cls) -> Optional[mysql.connector.connection.MySQLConnection]:
        """
        Obtiene una conexión MySQL del pool de conexiones o crea una nueva.
        
        Returns:
            MySQLConnection: Conexión a MySQL o None si hay error
        """
        if not hasattr(cls._local, "connection"):
            with cls._lock:
                try:
                    db_config = Config.DB_CONFIG['mysql']
                    connection = mysql.connector.connect(
                        host=db_config['host'],
                        port=db_config['port'],
                        user=db_config['user'],
                        password=db_config['password'],
                        database=db_config['database']
                    )
                    cls._local.connection = connection
                    logging.debug("Nueva conexión MySQL creada")
                except Error as e:
                    logging.error(f"Error al conectar a MySQL: {e}")
                    return None
        
        return cls._local.connection

    @classmethod
    def execute_query(cls, query: str, params: Optional[tuple] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Ejecuta una consulta SQL y retorna los resultados.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Lista de diccionarios con los resultados o None si hay error
        """
        connection = cls.get_connection()
        if connection is None:
            return None

        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
                logging.debug(f"Ejecutando query con parámetros: {query} - {params}")
            else:
                cursor.execute(query)
                logging.debug(f"Ejecutando query: {query}")

            result = cursor.fetchall()
            connection.commit()
            return result

        except Error as e:
            logging.error(f"Error al ejecutar query MySQL: {e}")
            if connection:
                connection.rollback()
            return None
        except Exception as e:
            logging.error(f"Error inesperado en MySQL: {e}")
            if connection:
                connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def execute_insert(cls, query: str, params: Optional[tuple] = None) -> Optional[int]:
        """
        Ejecuta una inserción y retorna el ID insertado.
        
        Args:
            query: Consulta SQL de inserción
            params: Parámetros para la inserción (opcional)
            
        Returns:
            ID del registro insertado o None si hay error
        """
        connection = cls.get_connection()
        if connection is None:
            return None

        cursor = None
        try:
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
                logging.debug(f"Ejecutando inserción con parámetros: {query} - {params}")
            else:
                cursor.execute(query)
                logging.debug(f"Ejecutando inserción: {query}")

            connection.commit()
            return cursor.lastrowid

        except Error as e:
            logging.error(f"Error al ejecutar inserción MySQL: {e}")
            if connection:
                connection.rollback()
            return None
        except Exception as e:
            logging.error(f"Error inesperado en MySQL: {e}")
            if connection:
                connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def execute_update(cls, query: str, params: Optional[tuple] = None) -> bool:
        """
        Ejecuta una actualización y retorna si fue exitosa.
        
        Args:
            query: Consulta SQL de actualización
            params: Parámetros para la actualización (opcional)
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        connection = cls.get_connection()
        if connection is None:
            return False

        cursor = None
        try:
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
                logging.debug(f"Ejecutando actualización con parámetros: {query} - {params}")
            else:
                cursor.execute(query)
                logging.debug(f"Ejecutando actualización: {query}")

            connection.commit()
            return True

        except Error as e:
            logging.error(f"Error al ejecutar actualización MySQL: {e}")
            if connection:
                connection.rollback()
            return False
        except Exception as e:
            logging.error(f"Error inesperado en MySQL: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    @classmethod
    def close_connection(cls) -> None:
        """Cierra la conexión a MySQL si existe"""
        if hasattr(cls._local, "connection"):
            try:
                if cls._local.connection.is_connected():
                    cls._local.connection.close()
                    logging.debug("Conexión MySQL cerrada")
            except Error as e:
                logging.error(f"Error al cerrar conexión MySQL: {e}")
            finally:
                delattr(cls._local, "connection")