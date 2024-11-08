# Archivo: data/mysql_menu_manager.py
import logging
from .mysql_database import MySQLDatabase

class MySQLMenuManager:
    def __init__(self):
        self.table_name = "menus"

    def get_menus_by_role_id(self, role_id):
        """
        Obtiene los menús asociados a un rol específico.
        """
        try:
            query = f"""
                SELECT m.id, m.name, m.url, m.icon 
                FROM {self.table_name} m
                INNER JOIN role_menu rm ON m.id = rm.menu_id
                WHERE rm.role_id = %s
                ORDER BY m.name
            """
            return MySQLDatabase.execute_query(query, (role_id,))
        except Exception as e:
            logging.exception(f"Error getting menus by role ID: {str(e)}")
            raise

    def get_all_menus(self):
        """
        Obtiene todos los menús del sistema.
        """
        try:
            query = f"""
                SELECT id, name, url, icon 
                FROM {self.table_name}
                ORDER BY name
            """
            return MySQLDatabase.execute_query(query)
        except Exception as e:
            logging.exception(f"Error getting all menus: {str(e)}")
            raise

    def create_menu(self, name, url, icon):
        """
        Crea un nuevo menú.
        """
        try:
            # Verificar si ya existe un menú con la misma URL
            check_query = f"SELECT id FROM {self.table_name} WHERE url = %s"
            existing = MySQLDatabase.execute_query(check_query, (url,))
            if existing:
                return False, "A menu with this URL already exists"

            # Insertar nuevo menú
            insert_query = f"""
                INSERT INTO {self.table_name} (name, url, icon) 
                VALUES (%s, %s, %s)
            """
            result = MySQLDatabase.execute_query(
                insert_query, 
                (name, url, icon),
                return_last_id=True
            )
            
            if result:
                # Obtener el menú recién creado
                new_menu = MySQLDatabase.execute_query(
                    f"SELECT * FROM {self.table_name} WHERE id = %s",
                    (result,)
                )
                return True, new_menu[0] if new_menu else None
            return False, "Failed to create menu"
        except Exception as e:
            logging.exception(f"Error creating menu: {str(e)}")
            raise

    def delete_menu(self, menu_id):
        """
        Elimina un menú y sus asociaciones con roles.
        """
        try:
            # Primero eliminar las asociaciones en role_menu
            delete_associations = """
                DELETE FROM role_menu WHERE menu_id = %s
            """
            MySQLDatabase.execute_query(delete_associations, (menu_id,))

            # Luego eliminar el menú
            delete_menu = f"DELETE FROM {self.table_name} WHERE id = %s"
            result = MySQLDatabase.execute_query(delete_menu, (menu_id,))
            return result is not None
        except Exception as e:
            logging.exception(f"Error deleting menu: {str(e)}")
            raise

    def update_menu(self, id, name, url, icon):
        """
        Actualiza un menú existente.
        """
        try:
            # Verificar si existe otro menú con la misma URL
            check_query = f"""
                SELECT id FROM {self.table_name} 
                WHERE url = %s AND id != %s
            """
            existing = MySQLDatabase.execute_query(check_query, (url, id))
            if existing:
                return False, "A menu with this URL already exists"

            query = f"""
                UPDATE {self.table_name} 
                SET name = %s, url = %s, icon = %s 
                WHERE id = %s
            """
            result = MySQLDatabase.execute_query(
                query, 
                (name, url, icon, id)
            )
            return result is not None, None
        except Exception as e:
            logging.exception(f"Error updating menu: {str(e)}")
            raise
