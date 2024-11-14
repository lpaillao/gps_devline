import os
import multiprocessing

# Configuración del servidor
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 1  # Un solo worker para evitar problemas con el servidor GPS
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

# Hooks del servidor
def on_starting(server):
    """Se ejecuta cuando el servidor está iniciando"""
    server.log.info("Starting GPS Tracking System")

def when_ready(server):
    """Se ejecuta cuando el servidor está listo"""
    server.log.info("Server is ready. Starting GPS Server...")

def on_exit(server):
    """Se ejecuta cuando el servidor está cerrando"""
    server.log.info("Shutting down GPS Tracking System")