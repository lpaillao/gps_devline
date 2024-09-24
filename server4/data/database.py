import sqlite3
import logging
from config import DATABASE_NAME
import threading

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