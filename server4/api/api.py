import os
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from threading import Event
import json
from datetime import datetime, timedelta
import logging
# Importar managers
from data.data_manager import DataManager
from data.mysql_user_manager import MySQLUserManager
from data.mysql_menu_manager import MySQLMenuManager
from data.mysql_role_menu_manager import MySQLRoleMenuManager
from data.mysql_dispositivo_gps_manager import MySQLDispositivoGPSManager
from data.mysql_asignacion_dispositivo_manager import MySQLAsignacionDispositivoManager
from data.mysql_ubicacion_manager import MySQLUbicacionManager
from data.mysql_role_manager import MySQLRoleManager
from data.mysql_empresa_manager import MySQLEmpresaManager
from data.mysql_tipo_gps_manager import MySQLTipoGPSManager

# Importar configuración
from config.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Inicializar Flask
app = Flask(__name__)

# Configurar CORS
CORS(app, **Config.get_cors_config())

# Configurar SocketIO
socketio = SocketIO(app, **Config.get_socketio_config())
_socket_instance = None
# Inicializar managers
user_manager = MySQLUserManager()
menu_manager = MySQLMenuManager()
role_menu_manager = MySQLRoleMenuManager()
dispositivo_gps_manager = MySQLDispositivoGPSManager()
tipo_gps_manager = MySQLTipoGPSManager()
asignacion_manager = MySQLAsignacionDispositivoManager()
empresa_manager = MySQLEmpresaManager()
ubicacion_manager = MySQLUbicacionManager()
role_manager = MySQLRoleManager()


@app.route('/')
def index():
    """
    Ruta principal que muestra información básica de la API
    """
    return jsonify({
        "name": "GPS Tracking System API",
        "version": "1.0",
        "status": "running",
        "documentation": "/api"
    })

# Health check endpoint
@app.route('/health')
@app.route('/api/health')
def health_check():
    """
    Health check endpoint para DigitalOcean App Platform
    """
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "running"
        }
    }

    # Verificar conexión a la base de datos
    try:
        user_manager.get_all_users()
        status["services"]["database"] = "connected"
    except Exception as e:
        status["services"]["database"] = "disconnected"
        status["status"] = "degraded"
        logging.error(f"Database health check failed: {str(e)}")

    # Verificar servidor GPS
    try:
        sock = socketio.socket(socketio.AF_INET, socketio.SOCK_STREAM)
        result = sock.connect_ex((Config.SERVER_CONFIG['host'], 
                                int(Config.SERVER_CONFIG['port'])))
        sock.close()
        status["services"]["gps_server"] = "running" if result == 0 else "stopped"
    except Exception as e:
        status["services"]["gps_server"] = "error"
        status["status"] = "degraded"
        logging.error(f"GPS server health check failed: {str(e)}")

    return jsonify(status), 200 if status["status"] == "healthy" else 500

# Middleware para logging
@app.before_request
def log_request_info():
    if request.path.startswith('/api'):
        logging.info(f'Headers: {dict(request.headers)}')
        logging.info(f'Body: {request.get_data()}')

# Middleware para manejo de errores
@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception("Error no manejado: ")
    return jsonify({
        "success": False,
        "message": "Error interno del servidor",
        "error": str(e)
    }), 500


@app.route('/api/login', methods=['POST'])
def login():
    """
    Maneja el proceso de login de usuarios.
    Espera un JSON con username y password.
    Retorna la información del usuario si el login es exitoso.
    """
    try:
        # Obtener datos JSON
        data = request.get_json()
        
        # Verificar si hay datos
        if not data:
            logging.error("No se recibieron datos en la solicitud")
            return jsonify({
                "success": False,
                "message": "No se recibieron datos"
            }), 400

        # Validar campos requeridos
        if not all(field in data for field in ['username', 'password']):
            logging.warning("Faltan campos requeridos en la solicitud")
            return jsonify({
                "success": False,
                "message": "Se requieren nombre de usuario y contraseña"
            }), 400

        # Intentar login
        logging.info(f"Intentando login para usuario: {data['username']}")
        user = user_manager.login(data['username'], data['password'])

        if not user:
            logging.warning(f"Credenciales inválidas para usuario: {data['username']}")
            return jsonify({
                "success": False,
                "message": "Credenciales inválidas"
            }), 401

        # Login exitoso
        logging.info(f"Login exitoso para usuario: {data['username']}")
        return jsonify({
            "success": True,
            "user": user,
            "message": "Login exitoso"
        }), 200

    except json.JSONDecodeError as e:
        logging.error(f"Error al decodificar JSON: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Formato de datos inválido"
        }), 400

    except Exception as e:
        logging.exception(f"Error inesperado durante el login: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500
@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        # Preflight request. Reply successfully:
        response = app.make_default_options_response()
    else:
        try:
            data = request.json
            logging.info(f"Registration attempt for username: {data.get('username')}")
            if not data or 'username' not in data or 'email' not in data or 'password' not in data:
                logging.warning("Missing required fields in registration request")
                return jsonify({"success": False, "message": "Missing required fields"}), 400
            
            nombre = data.get('nombre', data['username'])
            apellido = data.get('apellido', data['username'])
            success, message = user_manager.register(data['username'], data['email'], data['password'], nombre, apellido)
            if success:
                logging.info(f"Successful registration for user: {data['username']}")
                response = jsonify({"success": True, "message": message})
            else:
                logging.warning(f"Failed registration attempt for user: {data['username']} - {message}")
                response = jsonify({"success": False, "message": message}), 400
        except Exception as e:
            logging.exception(f"Registration error: {str(e)}")
            response = jsonify({"success": False, "message": f"An error occurred during registration: {str(e)}"}), 500

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': 'http://localhost:3000',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    if isinstance(response, tuple):
        response[0].headers.extend(headers)
    else:
        response.headers.extend(headers)
    return response

@app.route('/api/users', methods=['GET'])
def get_all_users():
    try:
        users = user_manager.get_all_users()
        return jsonify(users)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        result = user_manager.create_user(
            data['username'],
            data['email'],
            data['password'],
            data['role_id']
        )
        return jsonify({
            "success": result,
            "message": "User created successfully" if result else "Failed to create user"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    if user_manager.update_user(user_id, data['username'], data['email'], data['role_id']):
        return jsonify({"success": True, "message": "User updated successfully"})
    else:
        return jsonify({"success": False, "message": "User update failed"}), 400

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_manager.delete_user(user_id):
        return jsonify({"success": True, "message": "User deleted successfully"})
    else:
        return jsonify({"success": False, "message": "User deletion failed"}), 400

## ********************** ROLE MENU **********************

@app.route('/api/roles/<int:role_id>/menus', methods=['GET'])
def get_role_menus(role_id):
    try:
        menu_ids = role_menu_manager.get_role_menus(role_id)
        return jsonify({"success": True, "menu_ids": menu_ids})
    except Exception as e:
        logging.exception(f"Error getting role menus: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/roles/<int:role_id>/menus', methods=['POST'])
def update_role_menus(role_id):
    try:
        data = request.json
        if not data or 'menu_ids' not in data:
            return jsonify({"success": False, "message": "menu_ids required"}), 400
            
        success = role_menu_manager.update_role_menus(role_id, data['menu_ids'])
        return jsonify({
            "success": success,
            "message": "Role menus updated successfully" if success else "Failed to update role menus"
        })
    except Exception as e:
        logging.exception(f"Error updating role menus: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

## ********************** ubicacion manager **********************

@app.route('/api/ubicaciones', methods=['GET'])
def get_all_ubicaciones():
    """
    Obtiene todas las ubicaciones.
    """
    try:
        ubicaciones = ubicacion_manager.get_all_ubicaciones()
        return jsonify({
            "success": True,
            "ubicaciones": ubicaciones
        })
    except Exception as e:
        logging.exception(f"Error getting ubicaciones: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching ubicaciones."
        }), 500

@app.route('/api/ubicaciones', methods=['POST'])
def create_ubicacion():
    """
    Crea un nuevo registro de ubicación.
    """
    try:
        data = request.json
        required_fields = ['dispositivo_gps_id', 'latitud', 'longitud', 'fecha_hora']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "message": "Missing required fields: dispositivo_gps_id, latitud, longitud, fecha_hora"
            }), 400

        # Validación de datos
        try:
            latitud = float(data['latitud'])
            longitud = float(data['longitud'])
            fecha_hora = datetime.fromisoformat(data['fecha_hora'].replace('Z', '+00:00'))
            velocidad = float(data.get('velocidad')) if data.get('velocidad') is not None else None
            bateria = float(data.get('bateria')) if data.get('bateria') is not None else None
        except (ValueError, TypeError) as e:
            return jsonify({
                "success": False,
                "message": f"Invalid data format: {str(e)}"
            }), 400

        result = ubicacion_manager.create_ubicacion(
            data['dispositivo_gps_id'],
            latitud,
            longitud,
            fecha_hora,
            velocidad,
            bateria
        )

        if result:
            return jsonify({
                "success": True,
                "message": "Ubicación created successfully."
            })
        return jsonify({
            "success": False,
            "message": "Failed to create ubicación."
        }), 500
    except Exception as e:
        logging.exception(f"Error creating ubicación: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while creating the ubicación."
        }), 500

@app.route('/api/ubicaciones/dispositivo/<int:dispositivo_id>', methods=['GET'])
def get_ubicaciones_por_dispositivo(dispositivo_id):
    """
    Obtiene las ubicaciones de un dispositivo específico.
    """
    try:
        ubicaciones = ubicacion_manager.get_ubicaciones_por_dispositivo(dispositivo_id)
        return jsonify({
            "success": True,
            "ubicaciones": ubicaciones
        })
    except Exception as e:
        logging.exception(f"Error getting ubicaciones por dispositivo: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching ubicaciones for the dispositivo."
        }), 500

@app.route('/api/ubicaciones/dispositivo/<int:dispositivo_id>/ultima', methods=['GET'])
def get_ultima_ubicacion(dispositivo_id):
    """
    Obtiene la última ubicación de un dispositivo específico.
    """
    try:
        ubicacion = ubicacion_manager.get_ultima_ubicacion_por_dispositivo(dispositivo_id)
        if ubicacion:
            return jsonify({
                "success": True,
                "ubicacion": ubicacion
            })
        return jsonify({
            "success": False,
            "message": "No location found for this device."
        }), 404
    except Exception as e:
        logging.exception(f"Error getting última ubicación: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching the last location."
        }), 500

## ********************** MENU **********************

@app.route('/api/menus', methods=['GET'])
def get_all_menus():
    """
    Obtiene todos los menús.
    """
    try:
        menus = menu_manager.get_all_menus()
        return jsonify({
            "success": True,
            "menus": menus
        })
    except Exception as e:
        logging.exception(f"Error getting menus: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching menus."
        }), 500

@app.route('/api/menus/role/<int:role_id>', methods=['GET'])
def get_menus_by_role(role_id):
    """
    Obtiene los menús asociados a un rol específico.
    """
    try:
        menus = menu_manager.get_menus_by_role_id(role_id)
        return jsonify({
            "success": True,
            "menus": menus
        })
    except Exception as e:
        logging.exception(f"Error getting menus for role {role_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching menus for this role."
        }), 500

@app.route('/api/menus', methods=['POST'])
def create_menu():
    """
    Crea un nuevo menú.
    """
    try:
        data = request.json
        if not data or not all(k in data for k in ['name', 'url', 'icon']):
            return jsonify({
                "success": False,
                "message": "Name, URL, and icon are required."
            }), 400

        success, result = menu_manager.create_menu(
            data['name'],
            data['url'],
            data['icon']
        )

        if success:
            return jsonify({
                "success": True,
                "message": "Menu created successfully",
                "menu": result
            })
        return jsonify({
            "success": False,
            "message": result
        }), 400
    except Exception as e:
        logging.exception(f"Error creating menu: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while creating the menu."
        }), 500

@app.route('/api/menus/<int:id>', methods=['PUT'])
def update_menu(id):
    """
    Actualiza un menú existente.
    """
    try:
        data = request.json
        if not data or not all(k in data for k in ['name', 'url', 'icon']):
            return jsonify({
                "success": False,
                "message": "Name, URL, and icon are required."
            }), 400

        success, error = menu_manager.update_menu(
            id,
            data['name'],
            data['url'],
            data['icon']
        )

        if success:
            return jsonify({
                "success": True,
                "message": "Menu updated successfully"
            })
        return jsonify({
            "success": False,
            "message": error or "Failed to update menu"
        }), 400
    except Exception as e:
        logging.exception(f"Error updating menu: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while updating the menu."
        }), 500

@app.route('/api/menus/<int:id>', methods=['DELETE'])
def delete_menu(id):
    """
    Elimina un menú.
    """
    try:
        if menu_manager.delete_menu(id):
            return jsonify({
                "success": True,
                "message": "Menu deleted successfully"
            })
        return jsonify({
            "success": False,
            "message": "Failed to delete menu"
        }), 500
    except Exception as e:
        logging.exception(f"Error deleting menu: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while deleting the menu."
        }), 500
### ****************** TIPO GPS ******************
@app.route('/api/tipos-gps', methods=['GET'])
def get_all_tipos_gps():
    """
    Obtiene todos los tipos de GPS.
    """
    try:
        tipos = tipo_gps_manager.get_all_tipos_gps()
        return jsonify({
            "success": True,
            "tipos": tipos
        })
    except Exception as e:
        logging.exception(f"Error getting tipos GPS: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching tipos GPS."
        }), 500

@app.route('/api/tipos-gps', methods=['POST'])
def create_tipo_gps():
    """
    Crea un nuevo tipo de GPS.
    """
    try:
        data = request.json
        if not data or 'nombre' not in data:
            return jsonify({
                "success": False,
                "message": "Nombre is required."
            }), 400

        result = tipo_gps_manager.create_tipo_gps(data['nombre'])
        if result:
            return jsonify({
                "success": True,
                "message": "Tipo GPS created successfully."
            })
        return jsonify({
            "success": False,
            "message": "Failed to create tipo GPS."
        }), 500
    except Exception as e:
        logging.exception(f"Error creating tipo GPS: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while creating the tipo GPS."
        }), 500

@app.route('/api/tipos-gps/<int:id>', methods=['PUT'])
def update_tipo_gps(id):
    """
    Actualiza un tipo de GPS existente.
    """
    try:
        data = request.json
        if not data or 'nombre' not in data:
            return jsonify({
                "success": False,
                "message": "Nombre is required."
            }), 400

        result = tipo_gps_manager.update_tipo_gps(id, data['nombre'])
        if result:
            return jsonify({
                "success": True,
                "message": "Tipo GPS updated successfully."
            })
        return jsonify({
            "success": False,
            "message": "Failed to update tipo GPS."
        }), 500
    except Exception as e:
        logging.exception(f"Error updating tipo GPS: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while updating the tipo GPS."
        }), 500

@app.route('/api/tipos-gps/<int:id>', methods=['DELETE'])
def delete_tipo_gps(id):
    """
    Elimina un tipo de GPS.
    """
    try:
        result = tipo_gps_manager.delete_tipo_gps(id)
        if result:
            return jsonify({
                "success": True,
                "message": "Tipo GPS deleted successfully."
            })
        return jsonify({
            "success": False,
            "message": "Failed to delete tipo GPS."
        }), 500
    except Exception as e:
        logging.exception(f"Error deleting tipo GPS: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while deleting the tipo GPS."
        }), 500

### ****************** EMPRESAS ******************
@app.route('/api/empresas', methods=['GET'])
def get_all_empresas():
    """
    Obtiene todas las empresas.
    """
    try:
        empresas = empresa_manager.get_all_empresas()
        return jsonify({
            "success": True,
            "empresas": empresas
        })
    except Exception as e:
        logging.exception(f"Error getting empresas: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching empresas."
        }), 500

@app.route('/api/empresas', methods=['POST'])
def create_empresa():
    """
    Crea una nueva empresa.
    """
    try:
        data = request.json
        required_fields = ['nombre', 'direccion', 'telefono', 'email']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "message": "All fields (nombre, direccion, telefono, email) are required."
            }), 400

        # Validar email
        if not '@' in data['email']:
            return jsonify({
                "success": False,
                "message": "Invalid email format."
            }), 400

        result = empresa_manager.create_empresa(
            data['nombre'],
            data['direccion'],
            data['telefono'],
            data['email']
        )

        if result:
            return jsonify({
                "success": True,
                "message": "Empresa created successfully."
            })
        return jsonify({
            "success": False,
            "message": "Failed to create empresa."
        }), 500
    except Exception as e:
        logging.exception(f"Error creating empresa: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while creating the empresa."
        }), 500

@app.route('/api/empresas/<int:id>', methods=['PUT'])
def update_empresa(id):
    """
    Actualiza una empresa existente.
    """
    try:
        data = request.json
        required_fields = ['nombre', 'direccion', 'telefono', 'email']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "message": "All fields (nombre, direccion, telefono, email) are required."
            }), 400

        # Validar email
        if not '@' in data['email']:
            return jsonify({
                "success": False,
                "message": "Invalid email format."
            }), 400

        result = empresa_manager.update_empresa(
            id,
            data['nombre'],
            data['direccion'],
            data['telefono'],
            data['email']
        )

        if result:
            return jsonify({
                "success": True,
                "message": "Empresa updated successfully."
            })
        return jsonify({
            "success": False,
            "message": "Failed to update empresa."
        }), 500
    except Exception as e:
        logging.exception(f"Error updating empresa: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while updating the empresa."
        }), 500

@app.route('/api/empresas/<int:id>', methods=['DELETE'])
def delete_empresa(id):
    """
    Elimina una empresa.
    """
    try:
        result = empresa_manager.delete_empresa(id)
        if result:
            return jsonify({
                "success": True,
                "message": "Empresa deleted successfully."
            })
        return jsonify({
            "success": False,
            "message": "Failed to delete empresa."
        }), 500
    except Exception as e:
        logging.exception(f"Error deleting empresa: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while deleting the empresa."
        }), 500

@app.route('/api/empresas/<int:id>', methods=['GET'])
def get_empresa_by_id(id):
    """
    Obtiene una empresa específica por su ID.
    """
    try:
        empresa = empresa_manager.get_empresa_by_id(id)
        if empresa:
            return jsonify({
                "success": True,
                "empresa": empresa
            })
        return jsonify({
            "success": False,
            "message": "Empresa not found."
        }), 404
    except Exception as e:
        logging.exception(f"Error getting empresa: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching the empresa."
        }), 500


### ****************** ROLES ******************
@app.route('/api/roles', methods=['GET'])
def get_all_roles():
    """
    Obtiene todos los roles.
    """
    try:
        roles = role_manager.get_all_roles()
        return jsonify({
            "success": True,
            "roles": roles
        })
    except Exception as e:
        logging.exception(f"Error getting roles: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching roles."
        }), 500

@app.route('/api/roles', methods=['POST'])
def create_role():
    """
    Crea un nuevo rol.
    """
    try:
        data = request.json
        if not data or 'name' not in data:
            return jsonify({
                "success": False,
                "message": "Role name is required."
            }), 400

        success, result = role_manager.create_role(data['name'])
        
        if success:
            return jsonify({
                "success": True,
                "message": "Role created successfully",
                "role": result
            })
        return jsonify({
            "success": False,
            "message": result
        }), 400
    except Exception as e:
        logging.exception(f"Error creating role: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while creating the role."
        }), 500

@app.route('/api/roles/<int:id>', methods=['PUT'])
def update_role(id):
    """
    Actualiza un rol existente.
    """
    try:
        data = request.json
        if not data or 'name' not in data:
            return jsonify({
                "success": False,
                "message": "Role name is required."
            }), 400

        success, error = role_manager.update_role(id, data['name'])
        
        if success:
            return jsonify({
                "success": True,
                "message": "Role updated successfully"
            })
        return jsonify({
            "success": False,
            "message": error or "Failed to update role"
        }), 400
    except Exception as e:
        logging.exception(f"Error updating role: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while updating the role."
        }), 500

@app.route('/api/roles/<int:id>', methods=['DELETE'])
def delete_role(id):
    """
    Elimina un rol.
    """
    try:
        success, message = role_manager.delete_role(id)
        if success:
            return jsonify({
                "success": True,
                "message": message
            })
        return jsonify({
            "success": False,
            "message": message
        }), 400
    except Exception as e:
        logging.exception(f"Error deleting role: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while deleting the role."
        }), 500

### ++++++++++++++ ASIGNACIONES ++++++++++++++++
@app.route('/api/asignaciones', methods=['GET'])
def get_all_asignaciones():
    try:
        asignaciones = asignacion_manager.get_all_asignaciones()
        return jsonify({
            "success": True,
            "asignaciones": asignaciones
        })
    except Exception as e:
        logging.exception(f"Error getting asignaciones: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching asignaciones."
        }), 500

@app.route('/api/asignaciones', methods=['POST'])
def create_asignacion():
    try:
        data = request.json
        if not data or 'dispositivo_gps_id' not in data or \
           ('usuario_id' not in data and 'empresa_id' not in data):
            return jsonify({
                "success": False,
                "message": "Dispositivo GPS ID and either Usuario ID or Empresa ID are required."
            }), 400

        result = asignacion_manager.create_asignacion(
            data['dispositivo_gps_id'],
            data.get('usuario_id'),
            data.get('empresa_id')
        )
        
        if result:
            return jsonify({
                "success": True,
                "message": "Asignación created successfully."
            })
        return jsonify({
            "success": False,
            "message": "Failed to create asignación."
        }), 500
    except Exception as e:
        logging.exception(f"Error creating asignación: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while creating the asignación."
        }), 500

@app.route('/api/asignaciones/<int:id>', methods=['PUT'])
def update_asignacion(id):
    try:
        data = request.json
        if not data or 'dispositivo_gps_id' not in data or \
           ('usuario_id' not in data and 'empresa_id' not in data):
            return jsonify({
                "success": False,
                "message": "All required fields must be provided."
            }), 400

        result = asignacion_manager.update_asignacion(
            id,
            data['dispositivo_gps_id'],
            data.get('usuario_id'),
            data.get('empresa_id')
        )
        
        if result:
            return jsonify({
                "success": True,
                "message": "Asignación updated successfully."
            })
        return jsonify({
            "success": False,
            "message": "Failed to update asignación."
        }), 500
    except Exception as e:
        logging.exception(f"Error updating asignación: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while updating the asignación."
        }), 500

@app.route('/api/asignaciones/<int:id>', methods=['DELETE'])
def delete_asignacion(id):
    try:
        result = asignacion_manager.delete_asignacion(id)
        if result:
            return jsonify({
                "success": True,
                "message": "Asignación deleted successfully."
            })
        return jsonify({
            "success": False,
            "message": "Failed to delete asignación."
        }), 500
    except Exception as e:
        logging.exception(f"Error deleting asignación: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while deleting the asignación."
        }), 500

# Rutas adicionales para consultas específicas
@app.route('/api/asignaciones/usuario/<int:usuario_id>', methods=['GET'])
def get_asignaciones_por_usuario(usuario_id):
    try:
        asignaciones = asignacion_manager.get_asignaciones_por_usuario(usuario_id)
        return jsonify({
            "success": True,
            "asignaciones": asignaciones
        })
    except Exception as e:
        logging.exception(f"Error getting asignaciones por usuario: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching asignaciones."
        }), 500

@app.route('/api/asignaciones/empresa/<int:empresa_id>', methods=['GET'])
def get_asignaciones_por_empresa(empresa_id):
    try:
        asignaciones = asignacion_manager.get_asignaciones_por_empresa(empresa_id)
        return jsonify({
            "success": True,
            "asignaciones": asignaciones
        })
    except Exception as e:
        logging.exception(f"Error getting asignaciones por empresa: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching asignaciones."
        }), 500

@app.route('/api/asignaciones/dispositivo/<int:dispositivo_id>', methods=['GET'])
def get_asignacion_por_dispositivo(dispositivo_id):
    try:
        asignacion = asignacion_manager.get_asignacion_por_dispositivo(dispositivo_id)
        return jsonify({
            "success": True,
            "asignacion": asignacion
        })
    except Exception as e:
        logging.exception(f"Error getting asignación por dispositivo: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while fetching the asignación."
        }), 500


### ******************** API *************** ###


@app.route('/api/gps/<imei>')
def get_gps_data(imei):
    limit = request.args.get('limit', default=100, type=int)
    data = DataManager.get_data_by_imei(imei, limit)
    return jsonify(data)

@app.route('/api/gps/<imei>/latest')
def get_latest_location(imei):
    data = DataManager.get_latest_location(imei)
    return jsonify(data)

@app.route('/api/gps/<imei>/history')
def get_gps_history(imei):
    start_date = request.args.get('start_date', default=None, type=str)
    end_date = request.args.get('end_date', default=None, type=str)
    limit = request.args.get('limit', default=1000, type=int)

    if not start_date or not end_date:
        return jsonify({"error": "Se requieren fechas de inicio y fin"}), 400

    data = DataManager.get_gps_history(imei, start_date, end_date, limit)
    return jsonify(data)

@app.route('/api/gps/<imei>/summary')
def get_gps_summary(imei):
    data = DataManager.get_gps_summary(imei)
    return jsonify(data)

@app.route('/api/connected_devices')
def get_connected_devices():
    devices = DataManager.get_connected_devices()
    return jsonify(devices)

@app.route('/api/device_count')
def get_device_count():
    devices = DataManager.get_connected_devices()
    return jsonify({'count': len(devices)})

# Agregar estas nuevas rutas al archivo api.py

@app.route('/api/dispositivos', methods=['GET'])
def get_all_dispositivos_gps():
    try:
        dispositivos = dispositivo_gps_manager.get_all_dispositivos_gps()
        return jsonify({"success": True, "dispositivos": dispositivos})
    except Exception as e:
        logging.exception(f"Error getting dispositivos GPS: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "An error occurred while fetching dispositivos GPS."
        }), 500

@app.route('/api/dispositivos', methods=['POST'])
def create_dispositivo_gps():
    try:
        data = request.json
        if not all(key in data for key in ['imei', 'modelo', 'marca', 'tipo_gps_id']):
            return jsonify({
                "success": False, 
                "message": "All fields are required."
            }), 400

        result = dispositivo_gps_manager.create_dispositivo_gps(
            data['imei'], 
            data['modelo'], 
            data['marca'], 
            data['tipo_gps_id']
        )

        if result:
            return jsonify({
                "success": True, 
                "message": "Dispositivo GPS created successfully."
            })
        return jsonify({
            "success": False, 
            "message": "Failed to create dispositivo GPS."
        }), 500
    except Exception as e:
        logging.exception(f"Error creating dispositivo GPS: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "An error occurred while creating the dispositivo GPS."
        }), 500

@app.route('/api/dispositivos/<int:id>', methods=['PUT'])
def update_dispositivo_gps(id):
    try:
        data = request.json
        if not all(key in data for key in ['imei', 'modelo', 'marca', 'tipo_gps_id']):
            return jsonify({
                "success": False, 
                "message": "All fields are required."
            }), 400

        result = dispositivo_gps_manager.update_dispositivo_gps(
            id,
            data['imei'], 
            data['modelo'], 
            data['marca'], 
            data['tipo_gps_id']
        )

        if result:
            return jsonify({
                "success": True, 
                "message": "Dispositivo GPS updated successfully."
            })
        return jsonify({
            "success": False, 
            "message": "Failed to update dispositivo GPS."
        }), 500
    except Exception as e:
        logging.exception(f"Error updating dispositivo GPS: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "An error occurred while updating the dispositivo GPS."
        }), 500

@app.route('/api/dispositivos/<int:id>', methods=['DELETE'])
def delete_dispositivo_gps(id):
    try:
        result = dispositivo_gps_manager.delete_dispositivo_gps(id)
        if result:
            return jsonify({
                "success": True, 
                "message": "Dispositivo GPS deleted successfully."
            })
        return jsonify({
            "success": False, 
            "message": "Failed to delete dispositivo GPS."
        }), 500
    except Exception as e:
        logging.exception(f"Error deleting dispositivo GPS: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "An error occurred while deleting the dispositivo GPS."
        }), 500

# Manejo de conexión con WebSocket
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    emit('connection_response', {'message': 'Conexión exitosa con el servidor WebSocket'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

@socketio.on('subscribe')
def handle_subscribe(data):
    imei = data.get('imei', None)
    if imei:
        print(f'Cliente suscrito al IMEI: {imei}')
        socketio.emit('subscribed', {'imei': imei}, room=request.sid)
    else:
        print('IMEI no proporcionado')
        emit('subscription_error', {'error': 'IMEI no proporcionado'})

@app.route('/api/zones', methods=['GET', 'POST'])
def handle_zones():
    if request.method == 'GET':
        try:
            zones = DataManager.get_all_control_zones()
            return jsonify(zones), 200
        except Exception as e:
            logging.exception(f"Error al obtener zonas: {e}")
            return jsonify({"error": "Error interno del servidor al obtener zonas"}), 500
    elif request.method == 'POST':
        try:
            data = request.json
            logging.info(f"Datos recibidos para nueva zona: {data}")
            zone_id = DataManager.insert_control_zone(data['name'], data['coordinates'], data.get('imeis', []))
            if zone_id:
                return jsonify({'id': zone_id, 'message': 'Zona creada exitosamente'}), 201
            else:
                return jsonify({'error': 'Error al crear la zona'}), 500
        except Exception as e:
            logging.exception(f"Error al crear zona: {e}")
            return jsonify({"error": f"Error interno del servidor al crear zona: {str(e)}"}), 500


@app.route('/api/zones/<int:zone_id>', methods=['PUT', 'DELETE'])
def handle_zone(zone_id):
    if request.method == 'PUT':
        data = request.json
        success = DataManager.update_control_zone(zone_id, data['name'], data['coordinates'], data.get('imeis', []))
        if success:
            return jsonify({'message': 'Zona actualizada exitosamente'})
        else:
            return jsonify({'error': 'Error al actualizar la zona'}), 500
    elif request.method == 'DELETE':
        success = DataManager.delete_control_zone(zone_id)
        if success:
            return jsonify({'message': 'Zona eliminada exitosamente'})
        else:
            return jsonify({'error': 'Error al eliminar la zona'}), 500


@app.route('/api/zones/imei/<imei>')
def get_zones_for_imei(imei):
    zones = DataManager.get_zones_for_imei(imei)
    return jsonify(zones)

@app.teardown_appcontext
def shutdown_session(exception=None):
    DataManager.close()
# Emisión de actualización de datos GPS
#def emit_gps_update(imei, data):
#    socketio.emit('gps_update', {'imei': imei, 'data': data})

def emit_gps_update(imei, data):
    latitude = data['Location']['Latitude']
    longitude = data['Location']['Longitude']
    zones = DataManager.get_zones_for_imei(imei)
    current_zone = None
    for zone in zones:
        if point_in_polygon(latitude, longitude, zone['coordinates']):
            current_zone = zone['name']
            break
    
    data['current_zone'] = current_zone
    socketio.emit('gps_update', {'imei': imei, 'data': data})


def point_in_polygon(x, y, poly):
    """
    Determina si un punto (x, y) está dentro de un polígono.
    
    Args:
    x (float): Coordenada x del punto (longitud).
    y (float): Coordenada y del punto (latitud).
    poly (list): Lista de tuplas (x, y) que representan los vértices del polígono.
    
    Returns:
    bool: True si el punto está dentro del polígono, False en caso contrario.
    """
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

# Inicialización de la API

def start_api(shutdown_event: Event = None):
    """
    Iniciar la aplicación Flask con SocketIO
    
    Args:
        shutdown_event: Evento para controlar el apagado del servidor
    """
    global _socket_instance
    _socket_instance = socketio
    
    # Configurar Flask
    app.config.update(Config.get_flask_config())
    
    if os.getenv('FLASK_ENV') == 'production':
        # En producción, usar el puerto proporcionado por DigitalOcean
        port = int(os.getenv('PORT', '8080'))
        host = '0.0.0.0'
        debug = False
    else:
        # En desarrollo, usar la configuración normal
        api_config = Config.get_api_config()
        port = api_config['port']
        host = api_config['host']
        debug = api_config['debug']
    
    try:
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=False,
            cors_allowed_origins=Config.CORS_CONFIG['origins']
        )
    except Exception as e:
        logging.error(f"Error starting API server: {str(e)}")
        if shutdown_event:
            shutdown_event.set()
    finally:
        if shutdown_event:
            shutdown_event.set()

if __name__ == "__main__":
    # Si se ejecuta directamente, iniciar la API
    port = int(os.getenv('PORT', '8080'))
    socketio.run(app, host='0.0.0.0', port=port)