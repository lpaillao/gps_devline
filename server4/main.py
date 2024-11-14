from threading import Thread, Event
from config.config import Config
from server.gps_server import start_server
from api.api import app, socketio
import logging
import os

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

def start_gps_server():
    """Iniciar el servidor GPS en un hilo separado"""
    try:
        server_thread = Thread(target=start_server, args=(server_shutdown,))
        server_thread.daemon = True
        server_thread.start()
    except Exception as e:
        logging.error(f"Error starting GPS server: {e}")

def main():
    # Configurar logging
    Config.setup_logging()
    
    if os.getenv('FLASK_ENV') != 'production':
        setup_directories()
    
    # Iniciar servidor GPS
    start_gps_server()
    
    # En desarrollo, ejecutar con debug
    if os.getenv('FLASK_ENV') == 'development':
        socketio.run(
            app,
            host=Config.API_CONFIG['host'],
            port=int(os.getenv('PORT', Config.API_CONFIG['port'])),
            debug=Config.DEBUG
        )
    else:
        # En producción, devolver la aplicación para que la maneje gunicorn
        return app

if __name__ == "__main__":
    main()