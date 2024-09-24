from src.data.gps_data_store import GPSDataStore

class DataManager:
    def __init__(self):
        self.data_store = GPSDataStore()

    def save_gps_data(self, imei, records):
        self.data_store.store_gps_data(imei, records)

    def get_historical_data(self, imei, start_date, end_date):
        return self.data_store.get_historical_data(imei, start_date, end_date)

    def add_connected_gps(self, imei):
        self.data_store.add_connected_gps(imei)

    def remove_connected_gps(self, imei):
        self.data_store.remove_connected_gps(imei)

    def get_connected_gps(self):
        return self.data_store.get_connected_gps()

    def get_connection_history(self):
        return self.data_store.get_connection_history()