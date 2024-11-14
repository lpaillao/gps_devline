import os
import multiprocessing

# Configuración del servidor
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 1
worker_class = 'eventlet'
worker_connections = 1000
timeout = 120

# Logging
loglevel = 'info'
accesslog = '-'
errorlog = '-'
capture_output = True

# Configuración de proceso
daemon = False
pidfile = None
umask = 0
user = None
group = None

# Pre-carga de aplicación
preload_app = True

def on_starting(server):
    """Se ejecuta cuando el servidor está iniciando"""
    server.log.info("Starting GPS Tracking System")

def post_worker_init(worker):
    """Se ejecuta después de que cada worker se inicializa"""
    worker.log.info("Worker initialized")

def on_exit(server):
    """Se ejecuta cuando el servidor está cerrando"""
    server.log.info("Shutting down GPS Tracking System")