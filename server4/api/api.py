from flask import Flask, jsonify
from data.data_manager import DataManager
from config import API_HOST, API_PORT

app = Flask(__name__)

@app.route('/api/gps/<imei>')
def get_gps_data(imei):
    data = DataManager.get_data_by_imei(imei)
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