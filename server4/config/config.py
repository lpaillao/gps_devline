import os
from typing import List, Dict, Any, Union
from dotenv import load_dotenv
import logging
from pathlib import Path

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).parent.parent

# Cargar variables de entorno
load_dotenv(BASE_DIR / '.env')

def _get_boolean(value: str) -> bool:
    """Helper function para convertir strings a boolean"""
    return str(value).lower() in ('true', '1', 'yes', 'on')

def _get_list(value: str, separator: str = ',') -> List[str]:
    """Helper function para convertir strings a listas"""
    return [item.strip() for item in value.split(separator) if item.strip()]

class Config:
    """Configuración centralizada de la aplicación"""
    
    # Basic Configuration
    APP_NAME: str = os.getenv('APP_NAME', 'GPS Tracking System')
    FLASK_ENV: str = os.getenv('FLASK_ENV', 'development')
    DEBUG: bool = _get_boolean(os.getenv('DEBUG', 'True'))
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    LOG_DIR: Path = BASE_DIR / 'logs'
    STATIC_DIR: Path = BASE_DIR / 'static'

     # Server
    SERVER_CONFIG = {
        'host': os.getenv('SERVER_HOST', '0.0.0.0'),
        'port': int(os.getenv('SERVER_PORT', '6006')),
    }

    # API
    API_CONFIG = {
        'host': os.getenv('API_HOST', '0.0.0.0'),
        'port': int(os.getenv('PORT', '8080')),  # DigitalOcean usa la variable PORT
    }

    # Database
    DB_CONFIG = {
        'type': os.getenv('DB_TYPE', 'mysql'),
        'mysql': {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', '3306')),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', ''),
            'database': os.getenv('MYSQL_DATABASE', 'gps_devline'),
        },
        'sqlite': {
            'database': os.getenv('SQLITE_DATABASE_NAME', 'gps_tracking.db'),
            'path': os.getenv('SQLITE_PATH', str(BASE_DIR / 'data' / 'gps_tracking.db')),
        }
    }

    # CORS
    CORS_CONFIG = {
        'origins': [
            'https://gps-devline-ww883.ondigitalocean.app',
            'http://localhost:3000',
            'http://localhost:8080'
        ],
        'socket_origin': 'http://localhost:3000'  # Añadido para socket.io
    }

    # Logging
    LOG_CONFIG = {
        'level': os.getenv('LOG_LEVEL', 'DEBUG'),
        'format': os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        'file': os.getenv('LOG_FILE', str(LOG_DIR / 'gps_tracking.log'))
    }

    # Security
    SECURITY_CONFIG = {
        'secret_key': os.getenv('SECRET_KEY', 'your-secret-key-here'),
        'jwt_secret_key': os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-here'),
        'jwt_token_expires': int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600')),
    }

    # GPS Server
    GPS_CONFIG = {
        'server_url': os.getenv('GPS_SERVER_URL', ''),
        'timeout': int(os.getenv('GPS_SERVER_TIMEOUT', '30')),
        'max_connections': int(os.getenv('GPS_SERVER_MAX_CONNECTIONS', '100')),
    }

    @classmethod
    def get_flask_config(cls) -> Dict[str, Any]:
        """Obtiene la configuración para Flask"""
        return {
            'DEBUG': cls.DEBUG,
            'SECRET_KEY': cls.SECURITY_CONFIG['secret_key'],
            'JWT_SECRET_KEY': cls.SECURITY_CONFIG['jwt_secret_key'],
            'JWT_ACCESS_TOKEN_EXPIRES': cls.SECURITY_CONFIG['jwt_token_expires'],
        }

    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """Obtiene la configuración de CORS"""
        app_domain = os.getenv('APP_URL', 'http://localhost:3000')
        origins = [app_domain] + cls.CORS_CONFIG['origins']
        # Eliminar duplicados y None values
        origins = list(set(filter(None, origins)))
        
        return {
            "resources": {
                r"/api/*": {
                    "origins": origins,
                    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                    "allow_headers": ["Content-Type", "Authorization"],
                    "expose_headers": ["Content-Type", "Authorization"],
                    "supports_credentials": True,
                    "max_age": 120
                }
            }
        }


    @classmethod
    def get_socketio_config(cls) -> Dict[str, Any]:
        """Obtiene la configuración de SocketIO"""
        app_domain = os.getenv('APP_URL', 'http://localhost:3000')
        origins = [app_domain, cls.CORS_CONFIG['socket_origin']]
        # Eliminar duplicados y None values
        origins = list(set(filter(None, origins)))
        
        return {
            "cors_allowed_origins": origins,
            "async_mode": 'eventlet'
        }

    @classmethod
    def setup_logging(cls) -> None:
        """Configura el sistema de logging"""
        # Asegurar que el directorio de logs existe
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        
        log_level = getattr(logging, cls.LOG_CONFIG['level'].upper())
        logging.basicConfig(
            level=log_level,
            format=cls.LOG_CONFIG['format'],
            handlers=[
                logging.FileHandler(cls.LOG_CONFIG['file']),
                logging.StreamHandler()
            ]
        )

    @classmethod
    def get_db_url(cls) -> str:
        """Obtiene la URL de conexión a la base de datos"""
        if cls.DB_CONFIG['type'] == 'mysql':
            db = cls.DB_CONFIG['mysql']
            return f"mysql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}"
        return f"sqlite:///{cls.DB_CONFIG['sqlite']['path']}"
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """Obtiene la configuración de la API"""
        return {
            'host': cls.API_CONFIG['host'],
            'port': int(os.getenv('PORT', cls.API_CONFIG['port'])),  # Prioriza PORT de DigitalOcean
            'debug': cls.DEBUG
        }

    @classmethod
    def get_server_config(cls) -> Dict[str, Any]:
        """Obtiene la configuración del servidor GPS"""
        return {
            'host': cls.SERVER_CONFIG['host'],
            'port': cls.SERVER_CONFIG['port']
        }