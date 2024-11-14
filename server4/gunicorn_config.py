import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
backlog = 2048

# Worker processes
workers = 1  # Solo un worker para evitar problemas con el servidor GPS
worker_class = 'eventlet'
worker_connections = 1000
timeout = 120
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'gps-tracking-api'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Debugging
reload = False
reload_engine = 'auto'

# Server hooks
def on_starting(server):
    server.log.info("Starting GPS Tracking System")

def on_reload(server):
    server.log.info("Reloading GPS Tracking System")

def on_exit(server):
    server.log.info("Stopping GPS Tracking System")