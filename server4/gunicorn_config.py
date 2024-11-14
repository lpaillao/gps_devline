import multiprocessing
import os

# Configuración básica
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 2  # Reducido para evitar problemas de memoria
worker_class = 'eventlet'  # Necesario para WebSocket
worker_connections = 1000
timeout = 120  # Aumentado para evitar timeouts
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Configuración de rendimiento
graceful_timeout = 120
preload_app = True