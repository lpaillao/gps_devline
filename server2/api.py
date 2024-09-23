# server2/api.py
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from database import Database
from config import DATA_DIR
import os
import threading
from datetime import datetime, timedelta

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
db = Database(os.path.join(DATA_DIR, 'gps.db'))

# Importar AlertSystem después de definir socketio
#from alerts import AlertSystem
# alert_system = AlertSystem(socketio)

# Diccionario para almacenar sesiones de seguimiento activas
active_tracking = {}

@app.route('/gps/count', methods=['GET'])
def get_online_gps_count():
    count = db.get_online_gps_count()
    return jsonify({'conteo_gps_en_linea': count})

@app.route('/gps/recent', methods=['GET'])
def get_recent_connections():
    connections = db.get_recent_connections()
    return jsonify({'conexiones_recientes': connections})

@app.route('/gps/<imei>/latest', methods=['GET'])
def get_latest_gps_data(imei):
    data = db.get_latest_gps_data(imei)
    if data:
        return jsonify(data)
    return jsonify({'error': 'No se encontraron datos para este IMEI'}), 404

@app.route('/', methods=['GET'])
def home():
    return "¡La API del Servidor GPS está funcionando!"

@app.route('/gps/<imei>/track', methods=['GET'])
def track_gps(imei):
    return jsonify({"mensaje": f"Rastreando IMEI: {imei}", "estado": "éxito"})

def send_updates(imei):
    while imei in active_tracking:
        latest_data = db.get_latest_gps_data(imei)
        if latest_data:
            socketio.emit('actualizacion_gps', latest_data, room=imei)
        socketio.sleep(5)  # Enviar actualizaciones cada 5 segundos

@socketio.on('iniciar_seguimiento')
def handle_tracking(data):
    imei = data['imei']
    if imei not in active_tracking:
        active_tracking[imei] = True
        threading.Thread(target=send_updates, args=(imei,)).start()
    emit('estado_seguimiento', {'estado': 'iniciado', 'imei': imei})

@socketio.on('detener_seguimiento')
def handle_stop_tracking(data):
    imei = data['imei']
    if imei in active_tracking:
        del active_tracking[imei]
    emit('estado_seguimiento', {'estado': 'detenido', 'imei': imei})

@socketio.on('unirse')
def on_join(data):
    imei = data['imei']
    join_room(imei)
    emit('union_sala', {'estado': 'unido', 'imei': imei})

@socketio.on('salir')
def on_leave(data):
    imei = data['imei']
    leave_room(imei)
    emit('salida_sala', {'estado': 'salido', 'imei': imei})

@app.route('/gps/<imei>/history', methods=['GET'])
def get_route_history(imei):
    start_time = request.args.get('inicio', (datetime.now() - timedelta(hours=24)).isoformat())
    end_time = request.args.get('fin', datetime.now().isoformat())
    history = db.get_route_history(imei, start_time, end_time)
    return jsonify(history)

@app.route('/geofence', methods=['POST'])
def add_geofence():
    data = request.json
    db.add_geofence(data['nombre'], data['latitud'], data['longitud'], data['radio'])
    return jsonify({"mensaje": "Geovalla añadida con éxito", "estado": "éxito"})

@app.route('/geofences', methods=['GET'])
def get_geofences():
    geofences = db.get_geofences()
    return jsonify(geofences)

@app.route('/gps/<imei>/analytics', methods=['GET'])
def get_gps_analytics(imei):
    start_time = request.args.get('inicio', (datetime.now() - timedelta(hours=24)).isoformat())
    end_time = request.args.get('fin', datetime.now().isoformat())
    
    distance = db.get_distance_traveled(imei, start_time, end_time)
    time_in_motion = db.get_time_in_motion(imei, start_time, end_time)
    stop_count = db.get_stop_count(imei, start_time, end_time)

    return jsonify({
        'distancia_recorrida': distance,
        'tiempo_en_movimiento': time_in_motion,
        'cantidad_de_paradas': stop_count
    })

@socketio.on('connect')
def handle_connect():
    #alert_system.start()
    print('connected')

def start_api():
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    start_api()