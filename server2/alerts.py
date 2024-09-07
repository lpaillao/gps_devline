import threading
from database import Database
from config import DB_FILE
from flask_socketio import emit

class AlertSystem:
    def __init__(self, socketio):
        self.db = Database(DB_FILE)
        self.socketio = socketio

    def start(self):
        threading.Thread(target=self._check_alerts, daemon=True).start()

    def _check_alerts(self):
        while True:
            # Check for speed alerts
            gps_data = self.db.get_all_latest_gps_data()
            for data in gps_data:
                if data['speed'] > 100:  # Speed limit of 100 km/h
                    self._send_alert(data['imei'], 'speed', f"Speed limit exceeded: {data['speed']} km/h")

            # Check for geofence alerts
            geofences = self.db.get_geofences()
            for geofence in geofences:
                for data in gps_data:
                    distance = self._calculate_distance(geofence['latitude'], geofence['longitude'],
                                                        data['latitude'], data['longitude'])
                    if distance <= geofence['radius']:
                        self._send_alert(data['imei'], 'geofence', f"Entered geofence: {geofence['name']}")

            self.socketio.sleep(60)  # Check every 60 seconds

    def _send_alert(self, imei, alert_type, message):
        self.socketio.emit('alert', {'imei': imei, 'type': alert_type, 'message': message})

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        # Implement distance calculation here (e.g., using Haversine formula)
        # For now, we'll return a dummy value
        return 0  # This should be replaced with actual distance calculation