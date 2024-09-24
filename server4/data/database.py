import sqlite3
import logging
from config import DATABASE_NAME

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(DATABASE_NAME)
            self.cursor = self.conn.cursor()
            self.create_tables()
            logging.info("Connected to the database successfully")
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")

    def create_tables(self):
        self.cursor.execute('''
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
        self.conn.commit()

    def insert_gps_data(self, imei, data):
        try:
            self.cursor.execute('''
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
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error inserting GPS data: {e}")

    def get_gps_data_by_imei(self, imei, limit=100):
        try:
            self.cursor.execute('''
                SELECT * FROM gps_data
                WHERE imei = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (imei, limit))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error fetching GPS data: {e}")
            return []

    def get_connected_devices(self):
        try:
            self.cursor.execute('''
                SELECT DISTINCT imei FROM gps_data
                WHERE timestamp > datetime('now', '-5 minutes')
            ''')
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error fetching connected devices: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed")