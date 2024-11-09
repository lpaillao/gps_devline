import socket
import logging
from threading import Thread, Event
from .client_handler import ClientHandler
from config.config import Config

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return False
        except socket.error:
            return True

def start_server(shutdown_event: Event):
    """
    Inicia el servidor GPS.
    
    Args:
        shutdown_event: Evento para controlar el apagado del servidor
    """
    server_config = Config.get_server_config()
    
    if is_port_in_use(server_config['port']):
        logging.error(f"Port {server_config['port']} is already in use. Please choose a different port.")
        return

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((server_config['host'], server_config['port']))
        server.listen(5)
        server.settimeout(1.0)  # Timeout para poder verificar el evento de apagado
        
        logging.info(f"Server started successfully on {server_config['host']}:{server_config['port']}")
        print(f"Server is running on {server_config['host']}:{server_config['port']}")
        print("Waiting for GPS connections...")

        while not shutdown_event.is_set():
            try:
                conn, addr = server.accept()
                client_handler = ClientHandler(conn, addr)
                client_handler.daemon = True
                client_handler.start()
            except socket.timeout:
                continue
            except Exception as e:
                logging.error(f"Error accepting connection: {e}")
                if not shutdown_event.is_set():
                    continue
                break

    except socket.error as e:
        logging.error(f"Socket error: {e}")
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    finally:
        try:
            server.close()
            logging.info("Server shut down")
        except Exception as e:
            logging.error(f"Error closing server: {e}")