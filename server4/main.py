import os
import time
import socket
import logging
from threading import Thread, Event
from config.config import Config
from server.gps_server import start_server, GPSServer
from api.api import app, socketio

# Evento para controlar el ciclo de vida del servidor
server_shutdown = Event()
gps_server = None  # Variable global para el servidor GPS

def verify_port_available(port, host='0.0.0.0'):
    """Verifica si un puerto está disponible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0
    except Exception as e:
        logging.error(f"Error verificando puerto {port}: {e}")
        return False

def wait_for_server_start(host, port, timeout=10):
    """Espera a que el servidor GPS esté listo"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            if sock.connect_ex((host, port)) == 0:
                sock.close()
                return True
            sock.close()
        except:
            pass
        time.sleep(1)
    return False

def start_gps_server():
    """Inicia el servidor GPS"""
    global gps_server
    try:
        config = Config.get_server_config()
        host, port = config['host'], config['port']
        
        logging.info(f"Starting GPS server on {host}:{port}")
        
        # Verificar puerto
        if not verify_port_available(port, host):
            logging.error(f"Port {port} is already in use")
            return False
            
        # Iniciar servidor en un thread
        server_thread = Thread(
            target=start_server,
            args=(server_shutdown,),
            name="GPSServerThread"
        )
        server_thread.daemon = True
        server_thread.start()
        
        # Esperar a que el servidor inicie
        if wait_for_server_start(host, port):
            logging.info(f"GPS Server started successfully on port {port}")
            return True
        else:
            logging.error("GPS Server failed to start")
            return False
            
    except Exception as e:
        logging.error(f"Error starting GPS server: {e}")
        return False

def main():
    """Función principal"""
    try:
        # Configurar logging
        Config.setup_logging()
        logging.info(f"Starting {Config.APP_NAME}...")
        
        # Iniciar servidor GPS
        gps_started = start_gps_server()
        if not gps_started:
            logging.warning("Application will continue without GPS server")
            
        # Determinar modo de ejecución
        is_production = os.getenv('FLASK_ENV') == 'production'
        
        if is_production:
            logging.info("Starting in production mode")
            return app
        else:
            logging.info("Starting in development mode")
            port = int(os.getenv('PORT', Config.API_CONFIG['port']))
            socketio.run(
                app,
                host=Config.API_CONFIG['host'],
                port=port,
                debug=Config.DEBUG,
                use_reloader=False
            )
            
    except Exception as e:
        logging.error(f"Critical error: {e}")
        server_shutdown.set()
        raise
    finally:
        if server_shutdown.is_set():
            logging.info("Shutting down application")

if __name__ == "__main__":
    main()