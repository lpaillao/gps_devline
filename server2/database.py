import sqlite3
import logging
from datetime import datetime, timedelta

class Database:
    def __init__(self, archivo_db):
        self.archivo_db = archivo_db
        self.crear_tablas()

    def crear_tablas(self):
        conn = sqlite3.connect(self.archivo_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datos_gps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imei TEXT,
                marca_tiempo DATETIME,
                latitud REAL,
                longitud REAL,
                altitud INTEGER,
                angulo INTEGER,
                satelites INTEGER,
                velocidad INTEGER,
                prioridad INTEGER,
                datos_io TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conexiones_gps (
                imei TEXT PRIMARY KEY,
                ultima_conexion DATETIME,
                en_linea BOOLEAN
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS geovallas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                latitud REAL,
                longitud REAL,
                radio REAL
            )
        ''')
        conn.commit()
        conn.close()

    def agregar_geovalla(self, nombre, latitud, longitud, radio):
        conn = sqlite3.connect(self.archivo_db)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO geovallas (nombre, latitud, longitud, radio)
            VALUES (?, ?, ?, ?)
        ''', (nombre, latitud, longitud, radio))
        conn.commit()
        conn.close()

    def obtener_geovallas(self):
        conn = sqlite3.connect(self.archivo_db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM geovallas')
        resultados = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'nombre': r[1], 'latitud': r[2], 'longitud': r[3], 'radio': r[4]} for r in resultados]

    def insertar_datos_gps(self, datos):
        conn = sqlite3.connect(self.archivo_db)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO datos_gps (imei, marca_tiempo, latitud, longitud, altitud, angulo, satelites, velocidad, prioridad, datos_io)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datos['IMEI'],
            datos['DateTime'],
            datos['GPS Data']['Latitude'],
            datos['GPS Data']['Longitude'],
            datos['GPS Data']['Altitude'],
            datos['GPS Data']['Angle'],
            datos['GPS Data']['Satellites'],
            datos['GPS Data']['Speed'],
            datos['Priority'],
            str(datos['I/O Data'])
        ))
        conn.commit()
        conn.close()

    def actualizar_conexion_gps(self, imei, en_linea):
        conn = sqlite3.connect(self.archivo_db)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO conexiones_gps (imei, ultima_conexion, en_linea)
            VALUES (?, ?, ?)
        ''', (imei, datetime.now(), en_linea))
        conn.commit()
        conn.close()

    def obtener_conteo_gps_en_linea(self):
        conn = sqlite3.connect(self.archivo_db)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM conexiones_gps WHERE en_linea = 1')
        conteo = cursor.fetchone()[0]
        conn.close()
        return conteo

    def obtener_conexiones_recientes(self, limite=10):
        conn = sqlite3.connect(self.archivo_db)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT imei, ultima_conexion, en_linea 
            FROM conexiones_gps 
            ORDER BY ultima_conexion DESC 
            LIMIT ?
        ''', (limite,))
        resultados = cursor.fetchall()
        conn.close()
        return [{'imei': r[0], 'ultima_conexion': r[1], 'en_linea': bool(r[2])} for r in resultados]

    def obtener_ultimos_datos_gps(self, imei):
        conn = sqlite3.connect(self.archivo_db)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM datos_gps 
            WHERE imei = ? 
            ORDER BY marca_tiempo DESC 
            LIMIT 1
        ''', (imei,))
        resultado = cursor.fetchone()
        conn.close()
        if resultado:
            return {
                'id': resultado[0],
                'imei': resultado[1],
                'marca_tiempo': resultado[2],
                'latitud': resultado[3],
                'longitud': resultado[4],
                'altitud': resultado[5],
                'angulo': resultado[6],
                'satelites': resultado[7],
                'velocidad': resultado[8],
                'prioridad': resultado[9],
                'datos_io': resultado[10]
            }
        return None

    def obtener_historial_ruta(self, imei, tiempo_inicio, tiempo_fin):
        conn = sqlite3.connect(self.archivo_db)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT marca_tiempo, latitud, longitud, velocidad
            FROM datos_gps
            WHERE imei = ? AND marca_tiempo BETWEEN ? AND ?
            ORDER BY marca_tiempo
        ''', (imei, tiempo_inicio, tiempo_fin))
        resultados = cursor.fetchall()
        conn.close()
        return [{'marca_tiempo': r[0], 'latitud': r[1], 'longitud': r[2], 'velocidad': r[3]} for r in resultados]
    
    def obtener_distancia_recorrida(self, imei, tiempo_inicio, tiempo_fin):
        # Implementar cálculo de distancia basado en coordenadas GPS
        pass

    def obtener_tiempo_en_movimiento(self, imei, tiempo_inicio, tiempo_fin):
        conn = sqlite3.connect(self.archivo_db)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) * 5 / 60.0  -- Asumiendo puntos de datos cada 5 segundos, convertir a horas
            FROM datos_gps
            WHERE imei = ? AND marca_tiempo BETWEEN ? AND ? AND velocidad > 0
        ''', (imei, tiempo_inicio, tiempo_fin))
        resultado = cursor.fetchone()[0]
        conn.close()
        return resultado

    def obtener_conteo_paradas(self, imei, tiempo_inicio, tiempo_fin, duracion_parada=300):  # duracion_parada en segundos
        # Implementar lógica para contar paradas (períodos sin movimiento más largos que duracion_parada)
        pass

    def obtener_todos_los_ultimos_datos_gps(self):
        conn = sqlite3.connect(self.archivo_db)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t1.*
            FROM datos_gps t1
            INNER JOIN (
                SELECT imei, MAX(marca_tiempo) as max_marca_tiempo
                FROM datos_gps
                GROUP BY imei
            ) t2 ON t1.imei = t2.imei AND t1.marca_tiempo = t2.max_marca_tiempo
        ''')
        resultados = cursor.fetchall()
        conn.close()
        
        return [{
            'imei': r[1],
            'marca_tiempo': r[2],
            'latitud': r[3],
            'longitud': r[4],
            'altitud': r[5],
            'angulo': r[6],
            'satelites': r[7],
            'velocidad': r[8],
            'prioridad': r[9],
            'datos_io': r[10]
        } for r in resultados]