# server2/data_manager.py
import logging
from database import Database
from config import DB_FILE

class GestorDeDatos:
    def __init__(self):
        self.db = Database(DB_FILE)

    def guardar_datos(self, imei, registros):
        try:
            for registro in registros:
                self.db.insertar_datos_gps(registro)
            logging.info(f"Se guardaron {len(registros)} registros para el IMEI {imei}")
        except Exception as e:
            logging.error(f"Error al guardar datos para el IMEI {imei}: {e}")