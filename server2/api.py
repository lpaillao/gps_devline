from flask import Flask, jsonify
from database import Database
from config import DATA_DIR
import os

app = Flask(__name__)
db = Database(os.path.join(DATA_DIR, 'gps.db'))

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

def start_api():
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)