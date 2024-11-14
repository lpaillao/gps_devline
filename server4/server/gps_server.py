import socket
import logging
import threading
from typing import Dict, Set
from threading import Thread, Event, Lock
from .client_handler import ClientHandler
from config.config import Config

class GPSServer:
    def __init__(self):
        """Inicializa el servidor GPS"""
        self.server = None
        self.is_running = False
        self.clients: Dict[str, ClientHandler] = {}
        self.active_connections: Set[tuple] = set()
        self.clients_lock = Lock()
        self.connections_lock = Lock()
        
        # Configuración
        self.config = Config.get_server_config()
        self.host = self.config.get('host', '0.0.0.0')
        self.port = self.config.get('port', 6006)
        self.MAX_CONNECTIONS = 1000
        
    def start(self):
        """Inicia el servidor GPS en modo pasivo"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Vincular al puerto y comenzar a escuchar
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            self.is_running = True
            
            logging.info(f"GPS Server listening on {self.host}:{self.port}")
            logging.info("Waiting for GPS device connections...")
            
            # Iniciar el bucle principal de escucha
            self._listen_for_connections()
            
        except Exception as e:
            logging.error(f"Error starting GPS server: {e}")
            self.cleanup()
            raise

    def _listen_for_connections(self):
        """Bucle principal para escuchar conexiones"""
        while self.is_running:
            try:
                # Aceptar nuevas conexiones
                client_socket, client_address = self.server.accept()
                
                # Ignorar conexiones locales no deseadas
                if client_address[0] in ['127.0.0.1', 'localhost']:
                    logging.warning(f"Ignoring local connection attempt from {client_address}")
                    client_socket.close()
                    continue
                
                # Verificar límite de conexiones
                with self.connections_lock:
                    if len(self.active_connections) >= self.MAX_CONNECTIONS:
                        logging.warning(f"Connection limit reached. Rejecting {client_address}")
                        client_socket.close()
                        continue
                    self.active_connections.add(client_address)
                
                # Iniciar manejador de cliente en nuevo thread
                self._handle_new_connection(client_socket, client_address)
                
            except Exception as e:
                if self.is_running:
                    logging.error(f"Error accepting connection: {e}")
                continue

    def _handle_new_connection(self, client_socket: socket.socket, client_address: tuple):
        """Maneja una nueva conexión de dispositivo GPS"""
        try:
            logging.info(f"New GPS device connection from {client_address}")
            
            handler = ClientHandler(client_socket, client_address)
            handler.daemon = True
            handler.start()
            
            # Registrar el handler si la autenticación es exitosa
            def register_client(imei):
                if imei and imei != "unknown":
                    with self.clients_lock:
                        if imei in self.clients:
                            # Cerrar conexión anterior si existe
                            old_handler = self.clients[imei]
                            old_handler.is_running = False
                        self.clients[imei] = handler
                        logging.info(f"GPS device registered - IMEI: {imei}")
            
            # Configurar callback para cuando se complete la autenticación
            handler.on_auth_complete = register_client
            
        except Exception as e:
            logging.error(f"Error handling new connection {client_address}: {e}")
            try:
                client_socket.close()
            except:
                pass
            with self.connections_lock:
                self.active_connections.remove(client_address)

    def cleanup(self):
        """Limpia recursos del servidor"""
        self.is_running = False
        
        # Cerrar todas las conexiones activas
        with self.clients_lock:
            for client in self.clients.values():
                try:
                    client.is_running = False
                except:
                    pass
            self.clients.clear()
        
        # Cerrar el socket del servidor
        if self.server:
            try:
                self.server.close()
                logging.info("GPS Server shut down cleanly")
            except Exception as e:
                logging.error(f"Error closing server: {e}")

def start_server(shutdown_event: Event):
    """
    Inicia el servidor GPS
    
    Args:
        shutdown_event: Evento para controlar el apagado del servidor
    """
    try:
        # Verificar si el puerto ya está en uso
        server_config = Config.get_server_config()
        port = server_config.get('port', 6006)
        
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            test_socket.bind(('0.0.0.0', port))
            test_socket.close()
        except socket.error:
            logging.error(f"Port {port} is already in use")
            return False
            
        # Iniciar servidor GPS
        server = GPSServer()
        
        # Iniciar en un thread separado
        server_thread = Thread(target=server.start)
        server_thread.daemon = True
        server_thread.start()
        
        # Esperar señal de apagado
        while not shutdown_event.is_set():
            shutdown_event.wait(1)
        
        # Limpieza al recibir señal de apagado
        server.cleanup()
        return True
        
    except Exception as e:
        logging.error(f"Error in GPS server: {e}")
        return False