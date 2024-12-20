import sqlite3
import logging
import threading
import json
from datetime import datetime, timedelta
import pytz
from config.config import Config

class Database:
    _local = threading.local()
    _lock = threading.Lock()

    @classmethod
    def get_connection(cls):
        if not hasattr(cls._local, "connection"):
            with cls._lock:
                if not hasattr(cls._local, "connection"):
                    db_path = Config.DB_CONFIG['sqlite']['path']
                    cls._local.connection = sqlite3.connect(db_path, check_same_thread=False)
                    cls._local.connection.row_factory = sqlite3.Row
                    cls.create_tables(cls._local.connection)
        return cls._local.connection

    @classmethod
    def create_tables(cls, conn):
        cursor = conn.cursor()
        try:
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
                    name TEXT NOT NULL,
                    coordinates TEXT NOT NULL
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
            logging.info("Tablas creadas exitosamente")
        except sqlite3.Error as e:
            logging.error(f"Error creando tablas: {e}")
            conn.rollback()

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
            connection = cls.get_connection()
            cursor = connection.cursor()
            
            # Convertir las fechas a objetos datetime y ajustar el rango
            start_datetime = cls.parse_date(start_date)
            end_datetime = cls.parse_date(end_date) + timedelta(days=1) - timedelta(seconds=1)
            
            # Convertir a formato ISO 8601
            start_iso = start_datetime.isoformat()
            end_iso = end_datetime.isoformat()
            
            query = '''
                SELECT * FROM gps_data
                WHERE imei = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            cursor.execute(query, (imei, start_iso, end_iso, limit))
            
            results = [dict(row) for row in cursor.fetchall()]
            
            if not results:
                logging.info(f"No se encontraron datos para IMEI {imei} entre {start_iso} y {end_iso}")
            else:
                logging.info(f"Se encontraron {len(results)} registros para IMEI {imei}")
            
            return results
        except sqlite3.Error as e:
            logging.error(f"Error fetching GPS history: {e}")
            return []
    @staticmethod
    def parse_date(date_string):
        # Intentar varios formatos de fecha
        for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S'):
            try:
                return datetime.strptime(date_string, fmt).replace(tzinfo=pytz.UTC)
            except ValueError:
                continue
        raise ValueError(f"Formato de fecha no reconocido: {date_string}")
    
    @staticmethod
    def ensure_datetime_format(date_string):
        try:
            # Intentar parsear la fecha
            datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            return date_string
        except ValueError:
            # Si falla, asumir que solo se dio la fecha y agregar la hora
            return date_string + " 00:00:00"
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
                SELECT z.id, z.name, z.coordinates
                FROM zones z
                JOIN zone_imei zi ON z.id = zi.zone_id
                WHERE zi.imei = ?
            ''', (imei,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error fetching zones for IMEI: {e}")
            return []
    
    @classmethod
    def insert_zone(cls, name, coordinates, imeis=[]):
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO zones (name, coordinates) VALUES (?, ?)', (name, json.dumps(coordinates)))
            zone_id = cursor.lastrowid
            for imei in imeis:
                cursor.execute('''
                    INSERT OR REPLACE INTO zone_imei (zone_id, imei) 
                    VALUES (?, ?)
                ''', (zone_id, imei))
            conn.commit()
            logging.info(f"Zona '{name}' insertada con ID {zone_id}")
            return zone_id
        except sqlite3.Error as e:
            logging.error(f"Error insertando zona: {e}")
            conn.rollback()
            return None
        
    @classmethod
    def is_coordinate_in_zone(cls, lat, lon, zone_id):
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT coordinates FROM zones WHERE id = ?', (zone_id,))
            zone = cursor.fetchone()
            if zone:
                coordinates = json.loads(zone['coordinates'])
                return cls.point_in_polygon(lat, lon, coordinates)
            return False
        except sqlite3.Error as e:
            logging.error(f"Error checking coordinate in zone: {e}")
            return False
        
    @staticmethod
    def point_in_polygon(x, y, poly):
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
    
    @classmethod
    def update_zone(cls, zone_id, name, coordinates, imeis=[]):
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE zones SET name = ?, coordinates = ? WHERE id = ?', (name, json.dumps(coordinates), zone_id))
            cursor.execute('DELETE FROM zone_imei WHERE zone_id = ?', (zone_id,))
            for imei in imeis:
                cursor.execute('INSERT INTO zone_imei (zone_id, imei) VALUES (?, ?)', (zone_id, imei))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error updating zone: {e}")
            conn.rollback()
            return False

    @classmethod
    def delete_zone(cls, zone_id):
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM zones WHERE id = ?', (zone_id,))
            cursor.execute('DELETE FROM zone_imei WHERE zone_id = ?', (zone_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error deleting zone: {e}")
            conn.rollback()
            return False

    @classmethod
    def get_all_zones(cls):
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT z.id, z.name, z.coordinates, GROUP_CONCAT(zi.imei) as imeis
                FROM zones z
                LEFT JOIN zone_imei zi ON z.id = zi.zone_id
                GROUP BY z.id
            ''')
            zones = [dict(row) for row in cursor.fetchall()]
            for zone in zones:
                zone['coordinates'] = json.loads(zone['coordinates'])
                zone['imeis'] = zone['imeis'].split(',') if zone['imeis'] else []
            logging.info(f"Se obtuvieron {len(zones)} zonas")
            return zones
        except sqlite3.Error as e:
            logging.error(f"Error obteniendo zonas: {e}")
            return []

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

    @classmethod
    def close(cls):
        if hasattr(cls._local, "connection"):
            cls._local.connection.close()
            del cls._local.connection
        logging.info("Conexión a la base de datos cerrada")

