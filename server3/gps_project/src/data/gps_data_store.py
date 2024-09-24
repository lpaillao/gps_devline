import sqlite3
import json
from datetime import datetime
import threading
from src.config import CONFIG

class GPSDataStore:
    def __init__(self):
        self.database_path = CONFIG['database_path']
        self.local = threading.local()
        self.create_tables()

    def get_conn(self):
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.database_path)
        return self.local.conn

    def create_tables(self):
        conn = self.get_conn()
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS gps_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    imei TEXT,
                    timestamp DATETIME,
                    data JSON
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS gps_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    imei TEXT,
                    connected_at DATETIME,
                    disconnected_at DATETIME
                )
            ''')

    def store_gps_data(self, imei, records):
        conn = self.get_conn()
        with conn:
            for record in records:
                conn.execute('''
                    INSERT INTO gps_data (imei, timestamp, data)
                    VALUES (?, ?, ?)
                ''', (imei, record['DateTime'], json.dumps(record)))

    def get_historical_data(self, imei, start_date, end_date):
        conn = self.get_conn()
        query = '''
            SELECT data FROM gps_data
            WHERE imei = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        '''
        with conn:
            cursor = conn.execute(query, (imei, start_date, end_date))
            return [json.loads(row[0]) for row in cursor.fetchall()]

    def add_connected_gps(self, imei):
        conn = self.get_conn()
        with conn:
            conn.execute('''
                INSERT INTO gps_connections (imei, connected_at)
                VALUES (?, ?)
            ''', (imei, datetime.utcnow()))

    def remove_connected_gps(self, imei):
        conn = self.get_conn()
        with conn:
            conn.execute('''
                UPDATE gps_connections
                SET disconnected_at = ?
                WHERE imei = ? AND disconnected_at IS NULL
            ''', (datetime.utcnow(), imei))

    def get_connected_gps(self):
        conn = self.get_conn()
        query = '''
            SELECT DISTINCT imei FROM gps_connections
            WHERE disconnected_at IS NULL
        '''
        with conn:
            cursor = conn.execute(query)
            return [row[0] for row in cursor.fetchall()]

    def get_connection_history(self):
        conn = self.get_conn()
        query = '''
            SELECT imei, connected_at, disconnected_at
            FROM gps_connections
            ORDER BY connected_at DESC
        '''
        with conn:
            cursor = conn.execute(query)
            return [
                {
                    'imei': row[0],
                    'connected_at': row[1],
                    'disconnected_at': row[2]
                }
                for row in cursor.fetchall()
            ]