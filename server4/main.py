from threading import Thread, Event
from config.config import Config
from server.gps_server import start_server
from api.api import start_api
import logging
import os

# Evento para controlar el ciclo de vida del servidor
server_shutdown = Event()

def setup_directories():
    """Crear directorios necesarios si no existen"""
    directories = [
        Config.LOG_DIR,
        Config.STATIC_DIR,
        os.path.dirname(Config.DB_CONFIG['sqlite']['path'])
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    # Crear directorios necesarios
    setup_directories()
    
    # Configurar logging
    Config.setup_logging()
    
    print(f"Starting {Config.APP_NAME}...")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Iniciar el servidor GPS en un hilo separado
        server_thread = Thread(target=start_server, args=(server_shutdown,))
        server_thread.daemon = True
        server_thread.start()
        
        # Iniciar el servidor API (Flask)
        api_thread = Thread(target=start_api, args=(server_shutdown,))
        api_thread.daemon = True
        api_thread.start()
        
        # Mantener el programa principal ejecutándose
        while not server_shutdown.is_set():
            try:
                server_shutdown.wait(1)
            except KeyboardInterrupt:
                print("\nShutting down gracefully...")
                server_shutdown.set()
                break
            
    except Exception as e:
        print(f"Error: {str(e)}")
        server_shutdown.set()
        raise
    finally:
        server_shutdown.set()
        # Dar tiempo para que los hilos se cierren limpiamente
        import time
        time.sleep(2)
        print("Shutdown complete")

if __name__ == "__main__":
    main()