import unittest
from unittest.mock import patch, MagicMock
from src.data.data_manager import DataManager

class TestDataManager(unittest.TestCase):
    def setUp(self):
        self.data_manager = DataManager()

    @patch('src.data.gps_data_store.GPSDataStore.store_gps_data')
    def test_save_gps_data(self, mock_store_gps_data):
        imei = "123456789012345"
        records = [{"data": "test"}]
        self.data_manager.save_gps_data(imei, records)
        mock_store_gps_data.assert_called_once_with(imei, records)

    @patch('src.data.gps_data_store.GPSDataStore.get_historical_data')
    def test_get_historical_data(self, mock_get_historical_data):
        imei = "123456789012345"
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        self.data_manager.get_historical_data(imei, start_date, end_date)
        mock_get_historical_data.assert_called_once_with(imei, start_date, end_date)

    @patch('src.data.gps_data_store.GPSDataStore.add_connected_gps')
    def test_add_connected_gps(self, mock_add_connected_gps):
        imei = "123456789012345"
        self.data_manager.add_connected_gps(imei)
        mock_add_connected_gps.assert_called_once_with(imei)

    @patch('src.data.gps_data_store.GPSDataStore.remove_connected_gps')
    def test_remove_connected_gps(self, mock_remove_connected_gps):
        imei = "123456789012345"
        self.data_manager.remove_connected_gps(imei)
        mock_remove_connected_gps.assert_called_once_with(imei)

    @patch('src.data.gps_data_store.GPSDataStore.get_connected_gps')
    def test_get_connected_gps(self, mock_get_connected_gps):
        self.data_manager.get_connected_gps()
        mock_get_connected_gps.assert_called_once()

    @patch('src.data.gps_data_store.GPSDataStore.get_connection_history')
    def test_get_connection_history(self, mock_get_connection_history):
        self.data_manager.get_connection_history()
        mock_get_connection_history.assert_called_once()

if __name__ == '__main__':
    unittest.main()