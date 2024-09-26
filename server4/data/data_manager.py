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
    def get_latest_location(imei):
        return Database.get_latest_location(imei)

    @staticmethod
    def get_gps_history(imei, start_date, end_date, limit=1000):
        return Database.get_gps_history(imei, start_date, end_date, limit)

    @staticmethod
    def get_gps_summary(imei):
        return Database.get_gps_summary(imei)

    @staticmethod
    def get_connected_devices():
        return Database.get_connected_devices()
    
    # Métodos relacionados con Zonas de Control
    @staticmethod
    def insert_control_zone(name, coordinates, imeis=[]):
        try:
            zone_id = Database.insert_zone(name, coordinates, imeis)
            logging.info(f"Zone '{name}' inserted with ID {zone_id}")
            return zone_id
        except Exception as e:
            logging.error(f"Failed to insert control zone '{name}': {e}")
            return None

    @staticmethod
    def update_control_zone(zone_id, name, coordinates, imeis=[]):
        try:
            success = Database.update_zone(zone_id, name, coordinates, imeis)
            if success:
                logging.info(f"Zone ID {zone_id} updated successfully")
            else:
                logging.error(f"Failed to update zone ID {zone_id}")
            return success
        except Exception as e:
            logging.error(f"Failed to update control zone '{zone_id}': {e}")
            return False

    @staticmethod
    def delete_control_zone(zone_id):
        try:
            success = Database.delete_zone(zone_id)
            if success:
                logging.info(f"Zone ID {zone_id} deleted successfully")
            else:
                logging.error(f"Failed to delete zone ID {zone_id}")
            return success
        except Exception as e:
            logging.error(f"Failed to delete control zone '{zone_id}': {e}")
            return False

    @staticmethod
    def get_all_control_zones():
        try:
            zones = Database.get_all_zones()
            return zones
        except Exception as e:
            logging.error(f"Failed to retrieve control zones: {e}")
            return []

    @staticmethod
    def get_zones_for_imei(imei):
        try:
            zones = Database.get_zones_by_imei(imei)
            return zones
        except Exception as e:
            logging.error(f"Failed to retrieve zones for IMEI {imei}: {e}")
            return []
    @staticmethod
    def close():
        Database.close()