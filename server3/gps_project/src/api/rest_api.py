from flask import Flask, jsonify, request
from src.data.data_manager import DataManager
from src.config import CONFIG

app = Flask(__name__)
data_manager = DataManager()

@app.route('/gps/<imei>/history')
def get_gps_history(imei):
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    history = data_manager.get_historical_data(imei, start_date, end_date)
    return jsonify(history)

@app.route('/gps/connected')
def get_connected_gps():
    connected = data_manager.get_connected_gps()
    return jsonify(connected)

@app.route('/gps/connection-history')
def get_connection_history():
    history = data_manager.get_connection_history()
    return jsonify(history)

def start_rest_api():
    app.run(host=CONFIG['api_host'], port=CONFIG['api_port'])

if __name__ == '__main__':
    start_rest_api()