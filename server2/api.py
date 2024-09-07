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

# Import AlertSystem after socketio is defined
from alerts import AlertSystem
alert_system = AlertSystem(socketio)

# Dictionary to store active tracking sessions
active_tracking = {}

@app.route('/gps/count', methods=['GET'])
def get_online_gps_count():
    count = db.get_online_gps_count()
    return jsonify({'online_gps_count': count})

@app.route('/gps/recent', methods=['GET'])
def get_recent_connections():
    connections = db.get_recent_connections()
    return jsonify({'recent_connections': connections})

@app.route('/gps/<imei>/latest', methods=['GET'])
def get_latest_gps_data(imei):
    data = db.get_latest_gps_data(imei)
    if data:
        return jsonify(data)
    return jsonify({'error': 'No data found for this IMEI'}), 404

@app.route('/', methods=['GET'])
def home():
    return "GPS Server API is running!"

@app.route('/gps/<imei>/track', methods=['GET'])
def track_gps(imei):
    return jsonify({"message": f"Tracking IMEI: {imei}", "status": "success"})

def send_updates(imei):
    while imei in active_tracking:
        latest_data = db.get_latest_gps_data(imei)
        if latest_data:
            socketio.emit('gps_update', latest_data, room=imei)
        socketio.sleep(5)  # Send updates every 5 seconds

@socketio.on('start_tracking')
def handle_tracking(data):
    imei = data['imei']
    if imei not in active_tracking:
        active_tracking[imei] = True
        threading.Thread(target=send_updates, args=(imei,)).start()
    emit('tracking_status', {'status': 'started', 'imei': imei})

@socketio.on('stop_tracking')
def handle_stop_tracking(data):
    imei = data['imei']
    if imei in active_tracking:
        del active_tracking[imei]
    emit('tracking_status', {'status': 'stopped', 'imei': imei})

@socketio.on('join')
def on_join(data):
    imei = data['imei']
    join_room(imei)
    emit('room_join', {'status': 'joined', 'imei': imei})

@socketio.on('leave')
def on_leave(data):
    imei = data['imei']
    leave_room(imei)
    emit('room_leave', {'status': 'left', 'imei': imei})

@app.route('/gps/<imei>/history', methods=['GET'])
def get_route_history(imei):
    start_time = request.args.get('start', (datetime.now() - timedelta(hours=24)).isoformat())
    end_time = request.args.get('end', datetime.now().isoformat())
    history = db.get_route_history(imei, start_time, end_time)
    return jsonify(history)

@app.route('/geofence', methods=['POST'])
def add_geofence():
    data = request.json
    db.add_geofence(data['name'], data['latitude'], data['longitude'], data['radius'])
    return jsonify({"message": "Geofence added successfully", "status": "success"})

@app.route('/geofences', methods=['GET'])
def get_geofences():
    geofences = db.get_geofences()
    return jsonify(geofences)

@app.route('/gps/<imei>/analytics', methods=['GET'])
def get_gps_analytics(imei):
    start_time = request.args.get('start', (datetime.now() - timedelta(hours=24)).isoformat())
    end_time = request.args.get('end', datetime.now().isoformat())
    
    distance = db.get_distance_traveled(imei, start_time, end_time)
    time_in_motion = db.get_time_in_motion(imei, start_time, end_time)
    stop_count = db.get_stop_count(imei, start_time, end_time)

    return jsonify({
        'distance_traveled': distance,
        'time_in_motion': time_in_motion,
        'stop_count': stop_count
    })

@socketio.on('connect')
def handle_connect():
    alert_system.start()

def start_api():
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    start_api()