import logging
from database import Database
from config import DB_FILE

class DataManager:
    def __init__(self):
        self.db = Database(DB_FILE)

    def save_data(self, imei, records):
        try:
            for record in records:
                self.db.insert_gps_data(record)
            logging.info(f"Saved {len(records)} records for IMEI {imei}")
        except Exception as e:
            logging.error(f"Failed to save data for IMEI {imei}: {e}")