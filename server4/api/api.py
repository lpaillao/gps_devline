from flask import Flask, jsonify, request
from data.data_manager import DataManager
from config import API_HOST, API_PORT
from datetime import datetime, timedelta

app = Flask(__name__)

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

def start_api():
    app.run(host=API_HOST, port=API_PORT)