from database import Database
from config import DB_FILE

class GPSManager:
    def __init__(self):
        self.db = Database(DB_FILE)
|
    def connect(self, imei):
        self.db.actualizar_conexion_gps(imei, True)

    def disconnect(self, imei):
        self.db.actualizar_conexion_gps(imei, False)