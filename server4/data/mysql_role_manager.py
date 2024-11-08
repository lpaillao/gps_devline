# Archivo: data/mysql_role_manager.py
import logging
from .mysql_database import MySQLDatabase

class MySQLRoleManager:
    def __init__(self):
        self.table_name = "roles"

    def get_all_roles(self):
        """
        Obtiene todos los roles del sistema.
        """
        try:
            query = f"""
                SELECT r.id, r.name, 
                       COUNT(DISTINCT u.id) as user_count,
                       COUNT(DISTINCT rm.menu_id) as menu_count
                FROM {self.table_name} r
                LEFT JOIN users u ON r.id = u.role_id
                LEFT JOIN role_menu rm ON r.id = rm.role_id
                GROUP BY r.id, r.name
                ORDER BY r.name
            """
            return MySQLDatabase.execute_query(query)
        except Exception as e:
            logging.exception(f"Error getting all roles: {str(e)}")
            raise

    def create_role(self, name):
        """
        Crea un nuevo rol.
        """
        try:
            # Verificar si ya existe un rol con el mismo nombre
            check_query = f"SELECT id FROM {self.table_name} WHERE name = %s"
            existing = MySQLDatabase.execute_query(check_query, (name,))
            if existing:
                return False, "A role with this name already exists"

            # Insertar nuevo rol
            insert_query = f"INSERT INTO {self.table_name} (name) VALUES (%s)"
            result = MySQLDatabase.execute_query(
                insert_query, 
                (name,),
                return_last_id=True
            )
            
            if result:
                # Obtener el rol recién creado
                new_role = MySQLDatabase.execute_query(
                    f"SELECT * FROM {self.table_name} WHERE id = %s",
                    (result,)
                )
                return True, new_role[0] if new_role else None
            return False, "Failed to create role"
        except Exception as e:
            logging.exception(f"Error creating role: {str(e)}")
            raise

    def delete_role(self, role_id):
        """
        Elimina un rol si no está en uso.
        """
        try:
            # Verificar si el rol está en uso
            check_query = """
                SELECT 
                    COUNT(u.id) as user_count,
                    COUNT(rm.menu_id) as menu_count
                FROM roles r
                LEFT JOIN users u ON r.id = u.role_id
                LEFT JOIN role_menu rm ON r.id = rm.role_id
                WHERE r.id = %s
                GROUP BY r.id
            """
            usage = MySQLDatabase.execute_query(check_query, (role_id,))
            
            if usage and (usage[0]['user_count'] > 0 or usage[0]['menu_count'] > 0):
                return False, "Cannot delete role: it is still in use by users or menus"

            # Eliminar el rol
            delete_query = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = MySQLDatabase.execute_query(delete_query, (role_id,))
            
            if result is not None:
                return True, "Role deleted successfully"
            return False, "Failed to delete role"
        except Exception as e:
            logging.exception(f"Error deleting role: {str(e)}")
            raise

    def update_role(self, role_id, name):
        """
        Actualiza el nombre de un rol.
        """
        try:
            # Verificar si existe otro rol con el mismo nombre
            check_query = f"""
                SELECT id FROM {self.table_name} 
                WHERE name = %s AND id != %s
            """
            existing = MySQLDatabase.execute_query(check_query, (name, role_id))
            if existing:
                return False, "A role with this name already exists"

            query = f"UPDATE {self.table_name} SET name = %s WHERE id = %s"
            result = MySQLDatabase.execute_query(query, (name, role_id))
            return True if result is not None else False, None
        except Exception as e:
            logging.exception(f"Error updating role: {str(e)}")
            raise