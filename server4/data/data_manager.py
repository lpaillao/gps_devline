import logging
from .database import Database

class DataManager:
    @staticmethod
    def save_data(imei, records):
        try:
            for record in records:
                Database.insert_gps_data(imei, record)
            logging.info(f"Saved {len(records)} records for IMEI {imei}")
        except Exception as e:
            logging.error(f"Failed to save data for IMEI {imei}: {e}")

    @staticmethod
    def get_data_by_imei(imei, limit=100):
        return Database.get_gps_data_by_imei(imei, limit)

    @staticmethod
    def get_connected_devices():
        return Database.get_connected_devices()

    @staticmethod
    def close():
        Database.close()