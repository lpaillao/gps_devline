# server2/data_manager.py
import logging
from database import Database
from config import DB_FILE

class DataManager:
    def __init__(self):
        try:
            self.db = Database(DB_FILE)
            logging.info(f"Conexión a la base de datos establecida: {DB_FILE}")
        except Exception as e:
            logging.error(f"Error al inicializar la base de datos: {e}")
            raise

    def guardar_datos(self, imei, registros):
        if not registros:
            logging.warning(f"No hay registros para guardar para el IMEI {imei}")
            return

        try:
            registros_guardados = 0
            for registro in registros:
                try:
                    self.db.insertar_datos_gps(registro)
                    registros_guardados += 1
                except Exception as e:
                    logging.error(f"Error al guardar registro individual para IMEI {imei}: {e}")
                    # Continúa con el siguiente registro
            
            logging.info(f"Se guardaron {registros_guardados} de {len(registros)} registros para el IMEI {imei}")
        except Exception as e:
            logging.error(f"Error general al guardar datos para el IMEI {imei}: {e}")

    def obtener_ultimos_datos(self, imei, limite=1):
        try:
            datos = self.db.obtener_ultimos_datos_gps(imei, limite)
            logging.info(f"Se obtuvieron {len(datos)} registros recientes para el IMEI {imei}")
            return datos
        except Exception as e:
            logging.error(f"Error al obtener datos recientes para el IMEI {imei}: {e}")
            return []

    def obtener_estadisticas(self, imei):
        try:
            stats = self.db.obtener_estadisticas_gps(imei)
            logging.info(f"Se obtuvieron estadísticas para el IMEI {imei}")
            return stats
        except Exception as e:
            logging.error(f"Error al obtener estadísticas para el IMEI {imei}: {e}")
            return {}

    def cerrar_conexion(self):
        try:
            self.db.cerrar_conexion()
            logging.info("Conexión a la base de datos cerrada correctamente")
        except Exception as e:
            logging.error(f"Error al cerrar la conexión a la base de datos: {e}")