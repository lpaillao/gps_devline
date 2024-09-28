import logging
import struct
from datetime import datetime, timezone
import math


# IO ID Mapping (you should expand this based on your specific needs)
IO_ID_MAPPING = {
    1: 'Digital Input 1',
    2: 'Digital Input 2',
    3: 'Digital Input 3',
    4: 'Digital Input 4',
    # Add more mappings as needed
}

class Decoder:
    def __init__(self, payload, imei):
        self.payload = payload
        self.imei = imei
        self.index = 0

    def decode_data(self):
        try:
            logging.debug(f"Raw payload: {self.payload}")

            self.index = 16
            codec_id = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2

            if codec_id != 0x08:
                raise ValueError(f"Unsupported codec ID: {codec_id}")

            num_of_data = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2

            records = []
            for _ in range(num_of_data):
                record = self.parse_avl_record()
                if record:
                    records.append(record)

            # Verificar si hay suficientes datos para leer el número final de registros
            if len(self.payload) >= self.index + 4:
                num_of_data_end = int(self.payload[-4:-2], 16)
                if num_of_data != num_of_data_end:
                    logging.warning(f"Number of records mismatch: start={num_of_data}, end={num_of_data_end}")
            else:
                logging.warning("Insufficient data to read final record count")

            return records

        except Exception as e:
            logging.error(f"Error decoding data: {e}")
            return []

    def parse_avl_record(self):
        try:
            # Verificar si hay suficientes datos para un registro AVL completo
            if len(self.payload) < self.index + 16 + 2 + 8 + 8 + 4 + 4 + 2 + 4:
                logging.warning("Insufficient data for a complete AVL record")
                return None
            timestamp = struct.unpack('>Q', bytes.fromhex(self.payload[self.index:self.index + 16]))[0]
            timestamp = datetime.fromtimestamp(timestamp / 1000, timezone.utc)
            self.index += 16

            priority = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2

            longitude = struct.unpack('>i', bytes.fromhex(self.payload[self.index:self.index + 8]))[0] / 10000000.0
            self.index += 8
            latitude = struct.unpack('>i', bytes.fromhex(self.payload[self.index:self.index + 8]))[0] / 10000000.0
            self.index += 8
            altitude = struct.unpack('>H', bytes.fromhex(self.payload[self.index:self.index + 4]))[0]
            self.index += 4
            angle = struct.unpack('>H', bytes.fromhex(self.payload[self.index:self.index + 4]))[0]
            self.index += 4
            satellites = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2
            speed = struct.unpack('>H', bytes.fromhex(self.payload[self.index:self.index + 4]))[0]
            self.index += 4

            io_records = self.parse_io_data()

            return {
                "IMEI": self.imei,
                "DateTime": timestamp.isoformat(),
                "Priority": priority,
                "Location": {
                    "Longitude": longitude,
                    "Latitude": latitude,
                    "Altitude": altitude,
                    "Angle": angle,
                    "Satellites": satellites,
                    "Speed": speed,
                },
                "I/O Data": io_records
            }
        except Exception as e:
            logging.error(f"Error parsing AVL record: {e}")
            return None

    def parse_io_data(self):
        io_records = {}

        try:
            if len(self.payload) < self.index + 4:
                logging.warning("Insufficient data for IO header")
                return io_records
            event_io_id = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2
            io_records['Event IO ID'] = event_io_id

            n_total_id = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2

            for io_size in [1, 2, 4, 8]:
                n_items = int(self.payload[self.index:self.index + 2], 16)
                self.index += 2
                for _ in range(n_items):
                    io_id = int(self.payload[self.index:self.index + 2], 16)
                    self.index += 2
                    io_value = struct.unpack(f'>{"BHIQ"[io_size // 2]}', bytes.fromhex(self.payload[self.index:self.index + io_size * 2]))[0]
                    self.index += io_size * 2
                    io_name = IO_ID_MAPPING.get(io_id, f'IO ID {io_id}')
                    io_records[io_name] = io_value

            return io_records
        except Exception as e:
            logging.error(f"Error parsing IO data: {e}")
            return io_records
    

    def process_fleet_data(self, records):
        if len(records) < 2:
            return

        for i in range(1, len(records)):
            prev_record = records[i-1]
            curr_record = records[i]

            prev_time = datetime.fromisoformat(prev_record['DateTime'])
            curr_time = datetime.fromisoformat(curr_record['DateTime'])
            time_diff = (curr_time - prev_time).total_seconds() / 3600  # en horas

            distance = self.haversine_distance(
                prev_record['Location']['Latitude'], prev_record['Location']['Longitude'],
                curr_record['Location']['Latitude'], curr_record['Location']['Longitude']
            )

            avg_speed = distance / abs(time_diff) if time_diff != 0 else 0

            curr_record['Fleet Data'] = {
                'Distance from Last Point (km)': round(distance, 2),
                'Time since Last Point (hours)': round(time_diff, 2),
                'Average Speed (km/h)': round(avg_speed, 2),
                'Heading': self.get_heading(curr_record['Location']['Angle']),
                'Movement Status': self.get_movement_status(curr_record['Location']['Speed']),
                'Estimated Fuel Consumption (L)': round(distance * 0.3, 2)
            }

            curr_record['Alerts'] = self.check_for_alerts(curr_record, prev_record)


    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in kilometers

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    def get_heading(self, angle):
        headings = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        return headings[round(angle / 45) % 8]

    def get_movement_status(self, speed):
        if speed == 0:
            return "Stopped"
        elif speed < 10:
            return "Idle"
        elif speed < 60:
            return "Moving"
        else:
            return "Fast Moving"

    def check_for_alerts(self, curr_record, prev_record):
        alerts = []

        # Verificar cambios repentinos de velocidad
        if abs(curr_record['Location']['Speed'] - prev_record['Location']['Speed']) > 30:
            alerts.append("Sudden speed change detected")

        # Verificar geofence (coordenadas de ejemplo, ajustar según sea necesario)
        if not (-39.0 <= curr_record['Location']['Latitude'] <= -38.0 and
                -73.0 <= curr_record['Location']['Longitude'] <= -72.0):
            if curr_record['Location']['Latitude'] != 0 or curr_record['Location']['Longitude'] != 0:
                alerts.append("Vehicle outside designated area")

        # Verificar paradas prolongadas
        if (curr_record['Location']['Speed'] == 0 and
            prev_record['Location']['Speed'] == 0 and
            curr_record['Fleet Data']['Time since Last Point (hours)'] > 1):
            alerts.append("Extended stop detected")

        return alerts
