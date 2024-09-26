import sqlite3
import logging
from config import DATABASE_NAME
import threading
import json
class Database:
    _local = threading.local()

    @classmethod
    def get_connection(cls):
        if not hasattr(cls._local, "connection"):
            cls._local.connection = sqlite3.connect(DATABASE_NAME)
            cls._local.connection.row_factory = sqlite3.Row
            cls.create_tables(cls._local.connection)
        return cls._local.connection

    @classmethod
    def create_tables(cls, conn):
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gps_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imei TEXT,
                timestamp TEXT,
                latitude REAL,
                longitude REAL,
                altitude INTEGER,
                angle INTEGER,
                satellites INTEGER,
                speed INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS control_zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                coordinates TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zone_imei_association (
                zone_id INTEGER,
                imei TEXT,
                FOREIGN KEY (zone_id) REFERENCES control_zones (id) ON DELETE CASCADE,
                PRIMARY KEY (zone_id, imei)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                coordinates TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zone_imei (
                zone_id INTEGER,
                imei TEXT,
                FOREIGN KEY (zone_id) REFERENCES zones (id) ON DELETE CASCADE,
                PRIMARY KEY (zone_id, imei)
            )
        ''')

        conn.commit()

    @classmethod
    def insert_gps_data(cls, imei, data):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO gps_data (imei, timestamp, latitude, longitude, altitude, angle, satellites, speed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                imei,
                data['DateTime'],
                data['Location']['Latitude'],
                data['Location']['Longitude'],
                data['Location']['Altitude'],
                data['Location']['Angle'],
                data['Location']['Satellites'],
                data['Location']['Speed']
            ))
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error inserting GPS data: {e}")

    @classmethod
    def get_gps_data_by_imei(cls, imei, limit=100):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM gps_data
                WHERE imei = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (imei, limit))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error fetching GPS data: {e}")
            return []

    @classmethod
    def get_latest_location(cls, imei):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM gps_data
                WHERE imei = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (imei,))
            return dict(cursor.fetchone())
        except sqlite3.Error as e:
            logging.error(f"Error fetching latest location: {e}")
            return None

    @classmethod
    def get_gps_history(cls, imei, start_date, end_date, limit=1000):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM gps_data
                WHERE imei = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (imei, start_date, end_date, limit))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error fetching GPS history: {e}")
            return []

    @classmethod
    def get_gps_summary(cls, imei):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_records,
                    MIN(timestamp) as first_record,
                    MAX(timestamp) as last_record,
                    AVG(speed) as avg_speed,
                    MAX(speed) as max_speed,
                    AVG(altitude) as avg_altitude
                FROM gps_data
                WHERE imei = ?
            ''', (imei,))
            return dict(cursor.fetchone())
        except sqlite3.Error as e:
            logging.error(f"Error fetching GPS summary: {e}")
            return {}

    @classmethod
    def get_connected_devices(cls):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT imei FROM gps_data
                WHERE timestamp > datetime('now', '-5 minutes')
            ''')
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error fetching connected devices: {e}")
            return []

    @classmethod
    def close(cls):
        if hasattr(cls._local, "connection"):
            cls._local.connection.close()
            del cls._local.connection
    
    @classmethod
    def insert_control_zone(cls, name, coordinates, imeis=[]):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO control_zones (name, coordinates)
                VALUES (?, ?)
            ''', (name, json.dumps(coordinates)))
            zone_id = cursor.lastrowid
            
            for imei in imeis:
                cursor.execute('''
                    INSERT INTO zone_imei_association (zone_id, imei)
                    VALUES (?, ?)
                ''', (zone_id, imei))
            
            conn.commit()
            return zone_id
        except sqlite3.Error as e:
            logging.error(f"Error al insertar zona de control: {e}")
            return None

    @classmethod
    def get_all_control_zones(cls):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cz.id, cz.name, cz.coordinates, GROUP_CONCAT(zia.imei) as imeis
                FROM control_zones cz
                LEFT JOIN zone_imei_association zia ON cz.id = zia.zone_id
                GROUP BY cz.id
            ''')
            zones = cursor.fetchall()
            return [{
                'id': zone['id'],
                'name': zone['name'],
                'coordinates': json.loads(zone['coordinates']),
                'imeis': zone['imeis'].split(',') if zone['imeis'] else []
            } for zone in zones]
        except sqlite3.Error as e:
            logging.error(f"Error al obtener zonas de control: {e}")
            return []

    @classmethod
    def update_control_zone(cls, zone_id, name, coordinates, imeis=[]):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE control_zones
                SET name = ?, coordinates = ?
                WHERE id = ?
            ''', (name, json.dumps(coordinates), zone_id))
            
            cursor.execute('DELETE FROM zone_imei_association WHERE zone_id = ?', (zone_id,))
            
            for imei in imeis:
                cursor.execute('''
                    INSERT INTO zone_imei_association (zone_id, imei)
                    VALUES (?, ?)
                ''', (zone_id, imei))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error al actualizar zona de control: {e}")
            return False

    @classmethod
    def delete_control_zone(cls, zone_id):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM control_zones WHERE id = ?', (zone_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error al eliminar zona de control: {e}")
            return False

    @classmethod
    def get_zones_for_imei(cls, imei):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cz.id, cz.name, cz.coordinates
                FROM control_zones cz
                LEFT JOIN zone_imei_association zia ON cz.id = zia.zone_id
                WHERE zia.imei = ? OR zia.imei IS NULL
            ''', (imei,))
            zones = cursor.fetchall()
            return [{
                'id': zone['id'],
                'name': zone['name'],
                'coordinates': json.loads(zone['coordinates'])
            } for zone in zones]
        except sqlite3.Error as e:
            logging.error(f"Error al obtener zonas para IMEI: {e}")
            return []
    @staticmethod
    def insert_zone(name, coordinates, imeis=[]):
        try:
            connection = Database.get_connection()
            cursor = connection.cursor()
             # Convertir las coordenadas a JSON
            coordinates_json = json.dumps(coordinates)  # Convertir a JSON

            # Inserción de la zona en la tabla de zonas (modifica según tu esquema)
            cursor.execute(
            "INSERT INTO control_zones (name, coordinates) VALUES (?, ?)",  
            (name, coordinates_json)  # Usar la cadena JSON en lugar de la lista
            )
            zone_id = cursor.lastrowid
            
            # Relacionar los IMEIs con la zona
            for imei in imeis:
                cursor.execute(
                    "INSERT INTO zone_imei (zone_id, imei) VALUES (?, ?)",
                    (zone_id, imei)
                )
            
            connection.commit()
            return zone_id
        except Exception as e:
            print(f"Error al insertar zona: {e}")
            return None
        finally:
            connection.close()

    @staticmethod
    def update_zone(zone_id, name, coordinates, imeis=[]):
        try:
            connection = Database.get_connection()
            cursor = connection.cursor()

            # Actualizar la zona
            cursor.execute(
                "UPDATE zones SET name = ?, coordinates = ? WHERE id = ?",
                (name, coordinates, zone_id)
            )

            # Eliminar las relaciones de IMEIs anteriores
            cursor.execute(
                "DELETE FROM zone_imei WHERE zone_id = ?",
                (zone_id,)
            )

            # Insertar nuevas relaciones de IMEIs
            for imei in imeis:
                cursor.execute(
                    "INSERT INTO zone_imei (zone_id, imei) VALUES (?, ?)",
                    (zone_id, imei)
                )

            connection.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar zona: {e}")
            return False
        finally:
            connection.close()

    @staticmethod
    def delete_zone(zone_id):
        try:
            connection = Database.get_connection()
            cursor = connection.cursor()

            # Eliminar la zona
            cursor.execute("DELETE FROM zones WHERE id = ?", (zone_id,))
            
            # Eliminar las relaciones de IMEIs
            cursor.execute("DELETE FROM zone_imei WHERE zone_id = ?", (zone_id,))
            
            connection.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar zona: {e}")
            return False
        finally:
            connection.close()

    @staticmethod
    def get_all_zones():
        try:
            connection = Database.get_connection()
            cursor = connection.cursor()

            # Obtener todas las zonas
            cursor.execute("SELECT * FROM zones")
            zones = cursor.fetchall()

            return zones
        except Exception as e:
            print(f"Error al obtener zonas: {e}")
            return []
        finally:
            connection.close()

    @staticmethod
    def get_zones_by_imei(imei):
        try:
            connection = Database.get_connection()
            cursor = connection.cursor()

            # Obtener las zonas asociadas a un IMEI
            cursor.execute(
                """
                SELECT zones.* FROM zones
                JOIN zone_imei ON zones.id = zone_imei.zone_id
                WHERE zone_imei.imei = ?
                """,
                (imei,)
            )
            zones = cursor.fetchall()

            return zones
        except Exception as e:
            print(f"Error al obtener zonas para el IMEI {imei}: {e}")
            return []
        finally:
            connection.close()