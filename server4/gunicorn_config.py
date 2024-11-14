import multiprocessing
import os

# Configuración básica
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 2
worker_class = 'eventlet'
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True

# Configuración de rendimiento
graceful_timeout = 120
preload_app = True

# Configuración de cabeceras
forwarded_allow_ips = '*'
proxy_allow_ips = '*'

# Configuración de SSL
proxy_protocol = True