import os

# Obtener la ruta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Configurar la ruta del archivo de log relativa al directorio actual
log_file_path = os.path.join(current_dir, '..', 'logs', 'gps_server.log')

CONFIG = {
    'gps_host': '0.0.0.0',
    'gps_port': 6006,
    'api_host': '0.0.0.0',
    'api_port': 5000,
    'database_path': os.path.join(current_dir, '..', 'gps_data.db'),
    'log_file': log_file_path,
}