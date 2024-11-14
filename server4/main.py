from threading import Thread, Event
from config.config import Config
from server.gps_server import start_server
from api.api import app, socketio
import logging
import os
import socket
import time

# Evento para controlar el ciclo de vida del servidor
server_shutdown = Event()

def setup_directories():
    """Crear directorios necesarios si no existen"""
    if os.getenv('FLASK_ENV') != 'production':
        directories = [
            Config.LOG_DIR,
            Config.STATIC_DIR,
            os.path.dirname(Config.DB_CONFIG['sqlite']['path'])
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

def verify_port_available(host, port, timeout=1):
    """
    Verifica si un puerto está disponible
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0
    except:
        return True

def wait_for_server_start(host, port, timeout=30):
    """
    Espera hasta que el servidor GPS esté funcionando
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
            time.sleep(1)
        except:
            time.sleep(1)
    return False

def start_gps_server():
    """
    Iniciar el servidor GPS en un hilo separado y verificar su inicio
    
    Returns:
        bool: True si el servidor inició correctamente, False en caso contrario
    """
    try:
        server_config = Config.get_server_config()
        host = server_config['host']
        port = server_config['port']

        # Verificar si el puerto está disponible
        if not verify_port_available(host, port):
            logging.error(f"Port {port} is already in use")
            return False

        # Iniciar el servidor en un hilo separado
        server_thread = Thread(target=start_server, args=(server_shutdown,))
        server_thread.daemon = True
        server_thread.start()

        # Esperar a que el servidor inicie
        if wait_for_server_start(host, port):
            logging.info(f"GPS Server successfully started on {host}:{port}")
            return True
        else:
            logging.error("GPS Server failed to start within timeout period")
            return False

    except Exception as e:
        logging.error(f"Error starting GPS server: {e}")
        return False

def main():
    """
    Función principal que inicia todos los componentes de la aplicación
    """
    try:
        # Configurar logging
        Config.setup_logging()
        logging.info("Starting application...")
        
        # Configurar directorios en desarrollo
        if os.getenv('FLASK_ENV') != 'production':
            setup_directories()
        
        # Iniciar servidor GPS
        gps_server_started = start_gps_server()
        if not gps_server_started:
            logging.warning("Application will continue without GPS server")
        
        # Configurar el modo de ejecución
        if os.getenv('FLASK_ENV') == 'development':
            # Modo desarrollo con socketio
            port = int(os.getenv('PORT', Config.API_CONFIG['port']))
            host = Config.API_CONFIG['host']
            logging.info(f"Starting development server on {host}:{port}")
            
            socketio.run(
                app,
                host=host,
                port=port,
                debug=Config.DEBUG
            )
        else:
            # Modo producción para gunicorn
            logging.info("Starting production server")
            return app

    except Exception as e:
        logging.error(f"Critical error starting application: {e}")
        server_shutdown.set()
        raise

if __name__ == "__main__":
    main()