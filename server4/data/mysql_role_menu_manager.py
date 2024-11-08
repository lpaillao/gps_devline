# data/mysql_role_menu_manager.py
import logging
from .mysql_database import MySQLDatabase

class MySQLRoleMenuManager:
    def __init__(self):
        self.table_name = "role_menu"

    def get_role_menus(self, role_id):
        try:
            query = """
                SELECT rm.menu_id 
                FROM role_menu rm
                WHERE rm.role_id = %s
            """
            result = MySQLDatabase.execute_query(query, (role_id,))
            menu_ids = [row['menu_id'] for row in result] if result else []
            logging.info(f"Retrieved menu IDs for role {role_id}: {menu_ids}")
            return menu_ids
        except Exception as e:
            logging.exception(f"Error getting role menus: {str(e)}")
            raise

    def update_role_menus(self, role_id, menu_ids):
        try:
            # Start transaction
            MySQLDatabase.start_transaction()
            
            try:
                # Delete existing role-menu associations
                delete_query = "DELETE FROM role_menu WHERE role_id = %s"
                MySQLDatabase.execute_query(delete_query, (role_id,))
                
                # Insert new role-menu associations
                if menu_ids:
                    insert_query = "INSERT INTO role_menu (role_id, menu_id) VALUES (%s, %s)"
                    values = [(role_id, menu_id) for menu_id in menu_ids]
                    
                    for value in values:
                        MySQLDatabase.execute_query(insert_query, value)
                
                # Commit transaction
                MySQLDatabase.commit()
                logging.info(f"Successfully updated menus for role {role_id}: {menu_ids}")
                return True
                
            except Exception as e:
                # Rollback in case of error
                MySQLDatabase.rollback()
                raise
                
        except Exception as e:
            logging.exception(f"Error updating role menus: {str(e)}")
            raise

    def assign_menu_to_role(self, role_id, menu_id):
        try:
            # Check if association already exists
            check_query = """
                SELECT 1 FROM role_menu 
                WHERE role_id = %s AND menu_id = %s
            """
            exists = MySQLDatabase.execute_query(check_query, (role_id, menu_id))
            
            if exists:
                logging.info(f"Menu {menu_id} already assigned to role {role_id}")
                return True

            query = "INSERT INTO role_menu (role_id, menu_id) VALUES (%s, %s)"
            result = MySQLDatabase.execute_query(query, (role_id, menu_id))
            
            success = result is not None
            logging.info(f"{'Successfully assigned' if success else 'Failed to assign'} menu {menu_id} to role {role_id}")
            return success
            
        except Exception as e:
            logging.exception(f"Error assigning menu to role: {str(e)}")
            raise

    def remove_menu_from_role(self, role_id, menu_id):
        try:
            query = "DELETE FROM role_menu WHERE role_id = %s AND menu_id = %s"
            result = MySQLDatabase.execute_query(query, (role_id, menu_id))
            
            success = result is not None
            logging.info(f"{'Successfully removed' if success else 'Failed to remove'} menu {menu_id} from role {role_id}")
            return success
            
        except Exception as e:
            logging.exception(f"Error removing menu from role: {str(e)}")
            raise