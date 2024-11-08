import mysql.connector
from mysql.connector import Error
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

class MySQLDatabase:
    @staticmethod
    def get_connection():
        try:
            connection = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
            )
            return connection
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return None

    @staticmethod
    def execute_query(query, params=None):
        connection = MySQLDatabase.get_connection()
        if connection is None:
            return None

        try:
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
            return result
        except Error as e:
            print(f"Error executing MySQL query: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()