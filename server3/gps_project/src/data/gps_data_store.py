import sqlite3
import json
from datetime import datetime
from src.config import CONFIG

class GPSDataStore:
    def __init__(self):
        self.conn = sqlite3.connect(CONFIG['database_path'])
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS gps_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    imei TEXT,
                    timestamp DATETIME,
                    data JSON
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS gps_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    imei TEXT,
                    connected_at DATETIME,
                    disconnected_at DATETIME
                )
            ''')

    def store_gps_data(self, imei, records):
        with self.conn:
            for record in records:
                self.conn.execute('''
                    INSERT INTO gps_data (imei, timestamp, data)
                    VALUES (?, ?, ?)
                ''', (imei, record['DateTime'], json.dumps(record)))

    def get_historical_data(self, imei, start_date, end_date):
        query = '''
            SELECT data FROM gps_data
            WHERE imei = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        '''
        with self.conn:
            cursor = self.conn.execute(query, (imei, start_date, end_date))
            return [json.loads(row[0]) for row in cursor.fetchall()]

    def add_connected_gps(self, imei):
        with self.conn:
            self.conn.execute('''
                INSERT INTO gps_connections (imei, connected_at)
                VALUES (?, ?)
            ''', (imei, datetime.utcnow()))

    def remove_connected_gps(self, imei):
        with self.conn:
            self.conn.execute('''
                UPDATE gps_connections
                SET disconnected_at = ?
                WHERE imei = ? AND disconnected_at IS NULL
            ''', (datetime.utcnow(), imei))

    def get_connected_gps(self):
        query = '''
            SELECT DISTINCT imei FROM gps_connections
            WHERE disconnected_at IS NULL
        '''
        with self.conn:
            cursor = self.conn.execute(query)
            return [row[0] for row in cursor.fetchall()]

    def get_connection_history(self):
        query = '''
            SELECT imei, connected_at, disconnected_at
            FROM gps_connections
            ORDER BY connected_at DESC
        '''
        with self.conn:
            cursor = self.conn.execute(query)
            return [
                {
                    'imei': row[0],
                    'connected_at': row[1],
                    'disconnected_at': row[2]
                }
                for row in cursor.fetchall()
            ]