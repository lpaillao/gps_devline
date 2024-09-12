# server2/server.py
import socket
from client_handler import ClientHandler
from config import HOST, PORT
from utils import is_port_in_use
import logging

def start_server():
    if is_port_in_use(PORT):
        logging.error(f"El puerto {PORT} ya está en uso. Por favor, elija un puerto diferente.")
        return

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        logging.info(f"Servidor iniciado exitosamente en {HOST}:{PORT}")
        print(f"El servidor está funcionando en {HOST}:{PORT}")
        print("Esperando conexiones GPS...")

        while True:
            conn, addr = server.accept()
            ClientHandler(conn, addr).start()
    except socket.error as e:
        logging.error(f"Error de socket: {e}")
    except KeyboardInterrupt:
        logging.info("Servidor detenido por el usuario")
    finally:
        server.close()
        logging.info("Servidor apagado")