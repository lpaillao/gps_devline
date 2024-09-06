import socket
from client_handler import ClientHandler
from config import HOST, PORT
from utils import is_port_in_use
import logging

def start_server():
    if is_port_in_use(PORT):
        logging.error(f"Port {PORT} is already in use. Please choose a different port.")
        return

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        logging.info(f"Server started successfully on {HOST}:{PORT}")
        print(f"Server is running on {HOST}:{PORT}")
        print("Waiting for GPS connections...")

        while True:
            conn, addr = server.accept()
            ClientHandler(conn, addr).start()
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    finally:
        server.close()
        logging.info("Server shut down")