import socket
import logging
import threading
from typing import Dict, Set, Optional
from threading import Thread, Event, Lock
from .client_handler import ClientHandler
from config.config import Config

class GPSServerInstance:
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Implementación thread-safe del singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = GPSServer()
        return cls._instance

class GPSServer:
    def __init__(self):
        """Inicializa el servidor GPS"""
        self.server: Optional[socket.socket] = None
        self.is_running = False
        self.clients: Dict[str, ClientHandler] = {}
        self.active_connections: Set[tuple] = set()
        self.clients_lock = Lock()
        self.connections_lock = Lock()
        self.server_thread: Optional[Thread] = None
        
        # Cargar configuración
        self.config = Config.get_server_config()
        self.host = self.config['host']
        self.port = self.config['port']
        self.backlog = self.config['backlog']
        self.max_connections = self.config['max_connections']
        self.buffer_size = self.config['buffer_size']
        
        # Estado del servidor
        self._is_initialized = False
        
    def initialize(self) -> bool:
        """Inicializa el servidor si no está inicializado"""
        if self._is_initialized:
            return True
            
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Configuración adicional del socket
            if self.config.get('reuse_port', False):
                self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                
            # Configurar timeout
            self.server.settimeout(self.config['timeout'])
            
            # Vincular al puerto
            self.server.bind((self.host, self.port))
            self.server.listen(self.backlog)
            
            self._is_initialized = True
            return True
            
        except Exception as e:
            logging.error(f"Error initializing GPS server: {e}")
            return False
            
    def start(self) -> bool:
        """Inicia el servidor GPS si no está corriendo"""
        if self.is_running:
            logging.warning("GPS Server is already running")
            return True
            
        if not self._is_initialized and not self.initialize():
            return False
            
        try:
            self.is_running = True
            self.server_thread = Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            logging.info(f"GPS Server listening on {self.host}:{self.port}")
            logging.info("Waiting for GPS device connections...")
            return True
            
        except Exception as e:
            logging.error(f"Error starting GPS server: {e}")
            self.cleanup()
            return False
            
    def _run_server(self):
        """Bucle principal del servidor"""
        while self.is_running:
            try:
                # Aceptar conexiones con timeout
                try:
                    client_socket, client_address = self.server.accept()
                except socket.timeout:
                    continue
                    
                # Ignorar conexiones locales no deseadas
                if client_address[0] in ['127.0.0.1', 'localhost']:
                    logging.warning(f"Ignoring local connection attempt from {client_address}")
                    client_socket.close()
                    continue
                    
                # Verificar límite de conexiones
                with self.connections_lock:
                    if len(self.active_connections) >= self.max_connections:
                        logging.warning(f"Connection limit reached. Rejecting {client_address}")
                        client_socket.close()
                        continue
                    self.active_connections.add(client_address)
                    
                # Manejar nueva conexión
                self._handle_connection(client_socket, client_address)
                
            except Exception as e:
                if self.is_running:
                    logging.error(f"Error in server loop: {e}")
                    
    def _handle_connection(self, client_socket: socket.socket, client_address: tuple):
        """Maneja una nueva conexión de dispositivo GPS"""
        try:
            logging.info(f"New GPS device connection from {client_address}")
            
            handler = ClientHandler(client_socket, client_address)
            handler.daemon = True
            handler.start()
            
            # Registrar cliente autenticado
            def on_auth_complete(imei: str):
                if imei and imei != "unknown":
                    with self.clients_lock:
                        if imei in self.clients:
                            old_handler = self.clients[imei]
                            old_handler.is_running = False
                        self.clients[imei] = handler
                        logging.info(f"GPS device registered - IMEI: {imei}")
                        
            handler.on_auth_complete = on_auth_complete
            
        except Exception as e:
            logging.error(f"Error handling connection {client_address}: {e}")
            self._cleanup_connection(client_address, client_socket)
            
    def _cleanup_connection(self, address: tuple, socket: Optional[socket.socket] = None):
        """Limpia una conexión específica"""
        with self.connections_lock:
            if address in self.active_connections:
                self.active_connections.remove(address)
                
        if socket:
            try:
                socket.close()
            except:
                pass

    def cleanup(self):
        """Limpia todos los recursos del servidor"""
        self.is_running = False
        
        # Cerrar conexiones activas
        with self.clients_lock:
            for client in self.clients.values():
                try:
                    client.is_running = False
                except:
                    pass
            self.clients.clear()
            
        # Cerrar socket del servidor
        if self.server:
            try:
                self.server.close()
                logging.info("GPS Server shut down cleanly")
            except Exception as e:
                logging.error(f"Error closing server: {e}")
                
        self._is_initialized = False

def start_server(shutdown_event: Event) -> bool:
    """
    Inicia el servidor GPS
    
    Args:
        shutdown_event: Evento para controlar el apagado del servidor
    """
    try:
        # Obtener instancia única del servidor
        server = GPSServerInstance.get_instance()
        
        # Iniciar servidor
        if not server.start():
            return False
            
        # Esperar señal de apagado
        while not shutdown_event.is_set():
            shutdown_event.wait(1)
            
        # Limpieza al recibir señal de apagado
        server.cleanup()
        return True
        
    except Exception as e:
        logging.error(f"Error in GPS server: {e}")
        return False
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