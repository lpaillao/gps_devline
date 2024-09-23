# server2/gps_manager.py
from database import Database
from config import DB_FILE

class GPSManager:
    def __init__(self):
        self.db = Database(DB_FILE)

    def connect(self, imei):
        self.db.update_gps_connection(imei, True)

    def disconnect(self, imei):
        self.db.update_gps_connection(imei, False)