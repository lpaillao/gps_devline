import socket
import logging
from threading import Thread, Event
from .client_handler import ClientHandler
from config.config import Config
import time

class GPSServer:
    def __init__(self):
        self.server = None
        self.is_running = False
        self.active_connections = set()

    def cleanup(self):
        """Limpia recursos del servidor"""
        if self.server:
            try:
                self.server.close()
                logging.info("GPS Server shut down cleanly")
            except Exception as e:
                logging.error(f"Error closing GPS server: {e}")

    def handle_client(self, client_socket, client_address):
        """Maneja una nueva conexión de cliente"""
        self.active_connections.add(client_address)
        try:
            client_handler = ClientHandler(client_socket, client_address)
            client_handler.daemon = True
            client_handler.start()
        except Exception as e:
            logging.error(f"Error handling client {client_address}: {e}")
        finally:
            self.active_connections.remove(client_address)

def is_port_in_use(port):
    """
    Verifica si un puerto está en uso
    
    Args:
        port (int): Puerto a verificar
        
    Returns:
        bool: True si el puerto está en uso, False si está disponible
    """
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
        shutdown_event (Event): Evento para controlar el apagado del servidor
        
    Returns:
        bool: True si el servidor inició correctamente, False en caso contrario
    """
    server_config = Config.get_server_config()
    host = server_config['host']
    port = server_config['port']
    
    # Verificar puerto
    if is_port_in_use(port):
        logging.error(f"Port {port} is already in use")
        return False

    # Inicializar servidor
    gps_server = GPSServer()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Configurar servidor
        server.bind((host, port))
        server.listen(5)
        server.settimeout(1.0)
        
        gps_server.server = server
        gps_server.is_running = True
        
        logging.info(f"GPS Server started successfully on {host}:{port}")
        logging.info("Waiting for GPS connections...")

        # Bucle principal
        while not shutdown_event.is_set():
            try:
                client_socket, client_address = server.accept()
                gps_server.handle_client(client_socket, client_address)
                
            except socket.timeout:
                continue
            except Exception as e:
                if not shutdown_event.is_set():
                    logging.error(f"Error accepting connection: {e}")
                    continue
                break

        return True

    except socket.error as e:
        logging.error(f"Socket error: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False
    finally:
        gps_server.cleanup()