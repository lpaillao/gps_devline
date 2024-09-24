import socket
import logging
from threading import Thread
from src.server.client_thread import ClientThread

class GPSServer(Thread):
    def __init__(self, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.server_socket = None

    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            logging.info(f"GPS Server started on {self.host}:{self.port}")
            
            while True:
                client_sock, address = self.server_socket.accept()
                logging.info(f"New connection from {address}")
                ClientThread(client_sock, address).start()
        except Exception as e:
            logging.error(f"Error in GPS Server: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def stop(self):
        if self.server_socket:
            self.server_socket.close()