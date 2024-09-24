import logging
from .database import Database

class DataManager:
    def __init__(self):
        self.db = Database()
        self.db.connect()

    def save_data(self, imei, records):
        try:
            for record in records:
                self.db.insert_gps_data(imei, record)
            logging.info(f"Saved {len(records)} records for IMEI {imei}")
        except Exception as e:
            logging.error(f"Failed to save data for IMEI {imei}: {e}")

    def get_data_by_imei(self, imei, limit=100):
        return self.db.get_gps_data_by_imei(imei, limit)

    def get_connected_devices(self):
        return self.db.get_connected_devices()

    def close(self):
        self.db.close()