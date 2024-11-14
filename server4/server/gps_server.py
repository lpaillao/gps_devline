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
        self.clients: Dict[str, ClientHandler] = {}  # Diccionario de clientes por IMEI
        self.active_connections: Set[tuple] = set()  # Set de conexiones activas
        self.clients_lock = Lock()  # Lock para acceso seguro a clients
        self.connections_lock = Lock()  # Lock para acceso seguro a active_connections
        
        # Configuración
        self.MAX_CONNECTIONS = 1000  # Máximo número de conexiones simultáneas
        self.LISTEN_BACKLOG = 50     # Tamaño de la cola de conexiones pendientes
        
    def cleanup(self):
        """Limpia recursos del servidor"""
        with self.clients_lock:
            for client in self.clients.values():
                try:
                    client.is_running = False
                except:
                    pass
            self.clients.clear()
            
        if self.server:
            try:
                self.server.close()
                logging.info("GPS Server shut down cleanly")
            except Exception as e:
                logging.error(f"Error closing GPS server: {e}")

    def handle_client(self, client_socket: socket.socket, client_address: tuple):
        """
        Maneja una nueva conexión de cliente
        
        Args:
            client_socket: Socket del cliente
            client_address: Tupla (ip, puerto) del cliente
        """
        # Verificar límite de conexiones
        with self.connections_lock:
            if len(self.active_connections) >= self.MAX_CONNECTIONS:
                logging.warning(f"Connection limit reached. Rejecting {client_address}")
                client_socket.close()
                return
            self.active_connections.add(client_address)
            
        try:
            client_handler = ClientHandler(client_socket, client_address)
            client_handler.start()
            
            # Esperar a que se complete la autenticación
            client_handler.join(timeout=30)  # 30 segundos máximo para autenticación
            
            if client_handler.is_alive() and client_handler.imei != "unknown":
                # Autenticación exitosa, registrar cliente
                with self.clients_lock:
                    if client_handler.imei in self.clients:
                        # Si ya existe una conexión con este IMEI, cerrarla
                        old_handler = self.clients[client_handler.imei]
                        old_handler.is_running = False
                        logging.info(f"Replacing existing connection for IMEI {client_handler.imei}")
                    self.clients[client_handler.imei] = client_handler
                    logging.info(f"Client registered successfully - IMEI: {client_handler.imei}")
            else:
                # Autenticación fallida o timeout
                client_handler.is_running = False
                logging.warning(f"Authentication failed or timeout for {client_address}")
                
        except Exception as e:
            logging.error(f"Error handling client {client_address}: {e}")
        finally:
            with self.connections_lock:
                self.active_connections.remove(client_address)
                
    def remove_client(self, imei: str):
        """
        Elimina un cliente del registro
        
        Args:
            imei: IMEI del dispositivo a eliminar
        """
        with self.clients_lock:
            if imei in self.clients:
                del self.clients[imei]
                logging.info(f"Client removed - IMEI: {imei}")

def is_port_in_use(port: int) -> bool:
    """Verifica si un puerto está en uso"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return False
        except socket.error:
            return True

def start_server(shutdown_event: Event) -> bool:
    """
    Inicia el servidor GPS
    
    Args:
        shutdown_event: Evento para controlar el apagado del servidor
    
    Returns:
        bool: True si el servidor inició correctamente
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
        server.listen(gps_server.LISTEN_BACKLOG)
        server.settimeout(1.0)  # Timeout para permitir chequeo de shutdown_event
        
        gps_server.server = server
        gps_server.is_running = True
        
        logging.info(f"GPS Server started successfully on {host}:{port}")
        logging.info("Waiting for GPS connections...")

        # Bucle principal
        while not shutdown_event.is_set():
            try:
                client_socket, client_address = server.accept()
                
                # Crear thread para manejar cliente
                client_thread = Thread(
                    target=gps_server.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if not shutdown_event.is_set():
                    logging.error(f"Error accepting connection: {e}")
                continue

        return True

    except socket.error as e:
        logging.error(f"Socket error: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False
    finally:
        gps_server.cleanup()