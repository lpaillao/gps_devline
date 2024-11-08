import logging
from .mysql_database import MySQLDatabase
from werkzeug.security import generate_password_hash, check_password_hash


class MySQLUserManager:
    def __init__(self):
        self.table_name = "users"
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def _verify_password(self, stored_password, provided_password):
        """
        Verifica la contraseña con soporte para múltiples métodos de hash
        """
        try:
            # Primero intentar con check_password_hash de werkzeug
            return check_password_hash(stored_password, provided_password)
        except ValueError as e:
            self.logger.warning(f"Werkzeug hash check failed: {str(e)}, trying alternative methods")
            
            try:
                # Si el hash comienza con "scrypt", usar otro método
                if stored_password.startswith('scrypt:'):
                    # Implementar verificación scrypt
                    import hashlib
                    params = stored_password.split(':')
                    if len(params) == 4:
                        _, n, r, p = params
                        n, r, p = int(n), int(r), int(p)
                        salt = b'salt'  # Deberías usar el salt real almacenado
                        hash_len = 32
                        stored_hash = base64.b64decode(params[-1])
                        computed_hash = hashlib.scrypt(
                            provided_password.encode(),
                            salt=salt,
                            n=n,
                            r=r,
                            p=p,
                            dklen=hash_len
                        )
                        return stored_hash == computed_hash
                
                # Si el hash comienza con "pbkdf2", usar pbkdf2
                elif stored_password.startswith('pbkdf2:'):
                    return check_password_hash(stored_password, provided_password)
                
                # Método de fallback: comparación directa (no recomendado para producción)
                else:
                    self.logger.warning("Using fallback password verification method")
                    return stored_password == provided_password
                    
            except Exception as e:
                self.logger.error(f"Password verification error: {str(e)}")
                return False

    def login(self, username, password):
        """
        Autentica un usuario en el sistema.
        """
        try:
            self.logger.debug(f"Attempting login for user: {username}")
            
            if not username or not password:
                self.logger.warning("Empty username or password provided")
                return None
                
            query = """
                SELECT u.id, u.username, u.password, u.email, u.nombre, u.apellido, 
                       u.role_id, r.name as role_name
                FROM {0} u
                LEFT JOIN roles r ON u.role_id = r.id
                WHERE u.username = %s
            """.format(self.table_name)
            
            result = MySQLDatabase.execute_query(query, (username,))
            
            if not result or len(result) == 0:
                self.logger.warning(f"No user found with username: {username}")
                return None
            
            user = result[0]
            stored_password = user.get('password')
            
            if not stored_password:
                self.logger.error(f"No password hash found for user: {username}")
                return None
            
            if self._verify_password(stored_password, password):
                self.logger.info(f"Successful login for user: {username}")
                del user['password']
                return {
                    'id': user.get('id'),
                    'username': user.get('username'),
                    'email': user.get('email'),
                    'nombre': user.get('nombre'),
                    'apellido': user.get('apellido'),
                    'role_id': user.get('role_id'),
                    'role_name': user.get('role_name')
                }
            else:
                self.logger.warning(f"Invalid password for user: {username}")
                return None
                
        except Exception as e:
            self.logger.exception(f"Login error for user {username}: {str(e)}")
            raise

    def register(self, username, email, password, nombre=None, apellido=None):
        """
        Registra un nuevo usuario usando PBKDF2 como método de hash
        """
        try:
            check_query = f"SELECT id FROM {self.table_name} WHERE username = %s OR email = %s"
            existing_user = MySQLDatabase.execute_query(check_query, (username, email))
            
            if existing_user and len(existing_user) > 0:
                return False, "Username or email already exists"

            # Usar PBKDF2 específicamente
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            self.logger.info(f"Generated PBKDF2 hash for new user {username}")

            insert_query = f"""
                INSERT INTO {self.table_name} 
                (username, email, password, role_id, nombre, apellido) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            role_id = 2
            nombre = nombre or username
            apellido = apellido or username
            
            result = MySQLDatabase.execute_query(
                insert_query, 
                (username, email, hashed_password, role_id, nombre, apellido)
            )
            
            if result is not None:
                self.logger.info(f"Successfully registered new user: {username}")
                return True, "User registered successfully"
            else:
                self.logger.error(f"Failed to register new user: {username}")
                return False, "Failed to insert new user"
        except Exception as e:
            self.logger.exception(f"Registration error: {str(e)}")
            return False, f"An error occurred: {str(e)}"
    def get_all_users(self):
        """
        Obtiene todos los usuarios con información de sus roles.
        """
        try:
            query = f"""
                SELECT u.id, u.username, u.email, u.nombre, u.apellido,
                       u.role_id, r.name as role_name
                FROM {self.table_name} u
                INNER JOIN roles r ON u.role_id = r.id
                ORDER BY u.username
            """
            return MySQLDatabase.execute_query(query)
        except Exception as e:
            logging.exception(f"Error getting all users: {str(e)}")
            raise

    def create_user(self, username, email, password, role_id):
        """
        Crea un nuevo usuario (función administrativa).
        """
        try:
            # Verificar si el usuario ya existe
            check_query = f"SELECT id FROM {self.table_name} WHERE username = %s OR email = %s"
            existing_user = MySQLDatabase.execute_query(check_query, (username, email))
            
            if existing_user and len(existing_user) > 0:
                return False

            query = f"""
                INSERT INTO {self.table_name} 
                (username, email, password, role_id) 
                VALUES (%s, %s, %s, %s)
            """
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            result = MySQLDatabase.execute_query(
                query, 
                (username, email, hashed_password, role_id)
            )
            return result is not None
        except Exception as e:
            logging.exception(f"Error creating user: {str(e)}")
            raise

    def update_user(self, id, username, email, role_id):
        """
        Actualiza la información de un usuario.
        """
        try:
            # Verificar si el nuevo username o email ya existe para otro usuario
            check_query = f"""
                SELECT id FROM {self.table_name} 
                WHERE (username = %s OR email = %s) AND id != %s
            """
            existing_user = MySQLDatabase.execute_query(
                check_query, 
                (username, email, id)
            )
            
            if existing_user and len(existing_user) > 0:
                return False

            query = f"""
                UPDATE {self.table_name} 
                SET username = %s, email = %s, role_id = %s 
                WHERE id = %s
            """
            result = MySQLDatabase.execute_query(
                query, 
                (username, email, role_id, id)
            )
            return result is not None
        except Exception as e:
            logging.exception(f"Error updating user: {str(e)}")
            raise

    def delete_user(self, id):
        """
        Elimina un usuario del sistema.
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = MySQLDatabase.execute_query(query, (id,))
            return result is not None
        except Exception as e:
            logging.exception(f"Error deleting user: {str(e)}")
            raise

    def get_user_by_id(self, id):
        """
        Obtiene un usuario por su ID.
        """
        try:
            query = f"""
                SELECT u.id, u.username, u.email, u.nombre, u.apellido,
                       u.role_id, r.name as role_name
                FROM {self.table_name} u
                INNER JOIN roles r ON u.role_id = r.id
                WHERE u.id = %s
            """
            result = MySQLDatabase.execute_query(query, (id,))
            return result[0] if result else None
        except Exception as e:
            logging.exception(f"Error getting user by ID: {str(e)}")
            raise

    def validate_credentials(self, username, email):
        """
        Valida si un username o email ya están en uso.
        """
        try:
            query = f"""
                SELECT id, username, email 
                FROM {self.table_name} 
                WHERE username = %s OR email = %s
            """
            result = MySQLDatabase.execute_query(query, (username, email))
            
            if result and len(result) > 0:
                existing = result[0]
                if existing['username'] == username:
                    return False, "Username already exists"
                return False, "Email already exists"
            return True, None
        except Exception as e:
            logging.exception(f"Error validating credentials: {str(e)}")
            raise