import unittest
from unittest.mock import patch, MagicMock
from src.server.gps_server import GPSServer

class TestGPSServer(unittest.TestCase):
    @patch('socket.socket')
    def test_server_initialization(self, mock_socket):
        server = GPSServer('localhost', 6006)
        server.start()
        mock_socket.assert_called_once()
        mock_socket.return_value.bind.assert_called_once_with(('localhost', 6006))
        mock_socket.return_value.listen.assert_called_once()

    @patch('src.server.gps_server.ClientThread')
    @patch('socket.socket')
    def test_client_connection(self, mock_socket, mock_client_thread):
        server = GPSServer('localhost', 6006)
        mock_socket.return_value.accept.return_value = (MagicMock(), ('127.0.0.1', 12345))
        
        server.run()
        
        mock_client_thread.assert_called_once()
        mock_client_thread.return_value.start.assert_called_once()

if __name__ == '__main__':
    unittest.main()