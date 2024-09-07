import sqlite3
import logging
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gps_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imei TEXT,
                timestamp DATETIME,
                latitude REAL,
                longitude REAL,
                altitude INTEGER,
                angle INTEGER,
                satellites INTEGER,
                speed INTEGER,
                priority INTEGER,
                io_data TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gps_connections (
                imei TEXT PRIMARY KEY,
                last_connected DATETIME,
                is_online BOOLEAN
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS geofences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                latitude REAL,
                longitude REAL,
                radius REAL
            )
        ''')
        conn.commit()
        conn.close()

    def add_geofence(self, name, latitude, longitude, radius):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO geofences (name, latitude, longitude, radius)
            VALUES (?, ?, ?, ?)
        ''', (name, latitude, longitude, radius))
        conn.commit()
        conn.close()

    def get_geofences(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM geofences')
        results = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'name': r[1], 'latitude': r[2], 'longitude': r[3], 'radius': r[4]} for r in results]

    def insert_gps_data(self, data):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO gps_data (imei, timestamp, latitude, longitude, altitude, angle, satellites, speed, priority, io_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['IMEI'],
            data['DateTime'],
            data['GPS Data']['Latitude'],
            data['GPS Data']['Longitude'],
            data['GPS Data']['Altitude'],
            data['GPS Data']['Angle'],
            data['GPS Data']['Satellites'],
            data['GPS Data']['Speed'],
            data['Priority'],
            str(data['I/O Data'])
        ))
        conn.commit()
        conn.close()

    def update_gps_connection(self, imei, is_online):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO gps_connections (imei, last_connected, is_online)
            VALUES (?, ?, ?)
        ''', (imei, datetime.now(), is_online))
        conn.commit()
        conn.close()

    def get_online_gps_count(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM gps_connections WHERE is_online = 1')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_recent_connections(self, limit=10):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT imei, last_connected, is_online 
            FROM gps_connections 
            ORDER BY last_connected DESC 
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return [{'imei': r[0], 'last_connected': r[1], 'is_online': bool(r[2])} for r in results]

    def get_latest_gps_data(self, imei):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM gps_data 
            WHERE imei = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (imei,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                'id': result[0],
                'imei': result[1],
                'timestamp': result[2],
                'latitude': result[3],
                'longitude': result[4],
                'altitude': result[5],
                'angle': result[6],
                'satellites': result[7],
                'speed': result[8],
                'priority': result[9],
                'io_data': result[10]
            }
        return None
    def get_route_history(self, imei, start_time, end_time):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, latitude, longitude, speed
            FROM gps_data
            WHERE imei = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        ''', (imei, start_time, end_time))
        results = cursor.fetchall()
        conn.close()
        return [{'timestamp': r[0], 'latitude': r[1], 'longitude': r[2], 'speed': r[3]} for r in results]
    
    def get_distance_traveled(self, imei, start_time, end_time):
        # Implement distance calculation based on GPS coordinates
        pass

    def get_time_in_motion(self, imei, start_time, end_time):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) * 5 / 60.0  -- Assuming data points every 5 seconds, convert to hours
            FROM gps_data
            WHERE imei = ? AND timestamp BETWEEN ? AND ? AND speed > 0
        ''', (imei, start_time, end_time))
        result = cursor.fetchone()[0]
        conn.close()
        return result

    def get_stop_count(self, imei, start_time, end_time, stop_duration=300):  # stop_duration in seconds
        # Implement logic to count stops (periods of no movement longer than stop_duration)
        pass