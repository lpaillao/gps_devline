from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from data.data_manager import DataManager
from config import API_HOST, API_PORT
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

@app.route('/api/gps/<imei>')
def get_gps_data(imei):
    limit = request.args.get('limit', default=100, type=int)
    data = DataManager.get_data_by_imei(imei, limit)
    return jsonify(data)

@app.route('/api/gps/<imei>/latest')
def get_latest_location(imei):
    data = DataManager.get_latest_location(imei)
    return jsonify(data)

@app.route('/api/gps/<imei>/history')
def get_gps_history(imei):
    start_date = request.args.get('start_date', default=None, type=str)
    end_date = request.args.get('end_date', default=None, type=str)
    limit = request.args.get('limit', default=1000, type=int)

    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')

    data = DataManager.get_gps_history(imei, start_date, end_date, limit)
    return jsonify(data)

@app.route('/api/gps/<imei>/summary')
def get_gps_summary(imei):
    data = DataManager.get_gps_summary(imei)
    return jsonify(data)

@app.route('/api/connected_devices')
def get_connected_devices():
    devices = DataManager.get_connected_devices()
    return jsonify(devices)

@app.route('/api/device_count')
def get_device_count():
    devices = DataManager.get_connected_devices()
    return jsonify({'count': len(devices)})

# Manejo de conexión con WebSocket
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    emit('connection_response', {'message': 'Conexión exitosa con el servidor WebSocket'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

@socketio.on('subscribe')
def handle_subscribe(data):
    imei = data.get('imei', None)
    if imei:
        print(f'Cliente suscrito al IMEI: {imei}')
        socketio.emit('subscribed', {'imei': imei}, room=request.sid)
    else:
        print('IMEI no proporcionado')
        emit('subscription_error', {'error': 'IMEI no proporcionado'})

@app.route('/api/zones', methods=['GET', 'POST'])
def handle_zones():
    if request.method == 'GET':
        zones = DataManager.get_all_control_zones()
        return jsonify(zones)
    elif request.method == 'POST':
        data = request.json
        zone_id = DataManager.insert_control_zone(data['name'], data['coordinates'], data.get('imeis', []))
        if zone_id:
            return jsonify({'id': zone_id, 'message': 'Zona creada exitosamente'}), 201
        else:
            return jsonify({'error': 'Error al crear la zona'}), 500

@app.route('/api/zones/<int:zone_id>', methods=['PUT', 'DELETE'])
def handle_zone(zone_id):
    if request.method == 'PUT':
        data = request.json
        success = DataManager.update_control_zone(zone_id, data['name'], data['coordinates'], data.get('imeis', []))
        if success:
            return jsonify({'message': 'Zona actualizada exitosamente'})
        else:
            return jsonify({'error': 'Error al actualizar la zona'}), 500
    elif request.method == 'DELETE':
        success = DataManager.delete_control_zone(zone_id)
        if success:
            return jsonify({'message': 'Zona eliminada exitosamente'})
        else:
            return jsonify({'error': 'Error al eliminar la zona'}), 500


@app.route('/api/zones/imei/<imei>')
def get_zones_for_imei(imei):
    zones = DataManager.get_zones_for_imei(imei)
    return jsonify(zones)

# Emisión de actualización de datos GPS
#def emit_gps_update(imei, data):
#    socketio.emit('gps_update', {'imei': imei, 'data': data})

def emit_gps_update(imei, data):
    latitude = data['Location']['Latitude']
    longitude = data['Location']['Longitude']
    zones = DataManager.get_zones_for_imei(imei)
    current_zone = None
    for zone in zones:
        if point_in_polygon(latitude, longitude, zone['coordinates']):
            current_zone = zone['name']
            break
    
    data['current_zone'] = current_zone
    socketio.emit('gps_update', {'imei': imei, 'data': data})


def point_in_polygon(x, y, poly):
    """
    Determina si un punto (x, y) está dentro de un polígono.
    
    Args:
    x (float): Coordenada x del punto (longitud).
    y (float): Coordenada y del punto (latitud).
    poly (list): Lista de tuplas (x, y) que representan los vértices del polígono.
    
    Returns:
    bool: True si el punto está dentro del polígono, False en caso contrario.
    """
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

# Inicialización de la API
def start_api():
    socketio.run(app, host=API_HOST, port=API_PORT)
