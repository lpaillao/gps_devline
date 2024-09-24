import socket
from threading import Thread
from datetime import datetime, timezone
import struct
import binascii
import json
import os
import logging
import sys
import time
import math
# Global Variables
HOST = '0.0.0.0'
PORT = 6006
DATA_DIR = 'gps_data'

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("gps_server.log"),
                        logging.StreamHandler(sys.stdout)
                    ])

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

            # Saltar los primeros 8 bytes (4 bytes de ceros + 4 bytes de longitud de datos)
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

            self.process_fleet_data(records)

            num_of_data_end = int(self.payload[-4:-2], 16)
            if num_of_data != num_of_data_end:
                logging.warning(f"Number of records mismatch: start={num_of_data}, end={num_of_data_end}")

            return records

        except Exception as e:
            logging.error(f"Error decoding data: {e}")
            return None

    def parse_avl_record(self):
        try:
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
    def decode_imei(self, imei_hex):
        # Los primeros 2 bytes (4 caracteres hex) indican la longitud del IMEI
        imei_length = int(imei_hex[:4], 16)
        
        # El resto es el IMEI en formato texto (bytes)
        imei_text = bytes.fromhex(imei_hex[4:]).decode('ascii')
        
        # Verificar que la longitud coincida
        if len(imei_text) != imei_length:
            raise ValueError(f"IMEI length mismatch: expected {imei_length}, got {len(imei_text)}")
        
        # Formatear como IMEI estándar
        return f"{imei_text[:3]}-{imei_text[3:5]}-{imei_text[5:9]}-{imei_text[9:12]}-{imei_text[12:]}"


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

class DataManager:
    def __init__(self):
        self.ensure_data_dir()

    def ensure_data_dir(self):
        if not os.path.exists(DATA_DIR):
            try:
                os.makedirs(DATA_DIR)
                logging.info(f"Created data directory: {DATA_DIR}")
            except Exception as e:
                logging.error(f"Failed to create data directory: {e}")
                raise

    def save_data(self, imei, records):
        filename = os.path.join(DATA_DIR, f"{imei}.json")
        mode = 'a' if os.path.exists(filename) else 'w'
        try:
            with open(filename, mode) as f:
                json.dump(records, f, indent=2)
                f.write('\n')  # Add a newline for readability between records
            logging.info(f"Saved {len(records)} records for IMEI {imei}")
        except Exception as e:
            logging.error(f"Failed to save data for IMEI {imei}: {e}")

class ClientThread(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.imei = "unknown"
        self.data_manager = DataManager()

    def run(self):
        logging.info(f"New connection from {self.addr}")
        try:
            self.handle_authentication()
            self.handle_data()
        except Exception as e:
            logging.error(f"Error handling client {self.addr}: {e}")
        finally:
            self.conn.close()
            logging.info(f"Connection closed for {self.addr}")

    def handle_authentication(self):
        logging.info("Waiting for device authentication...")
        buff = self.conn.recv(8192)
        received = binascii.hexlify(buff).decode()
        logging.debug(f"Received authentication data: {received}")
        if len(received) > 2:
            # Decodificar el IMEI correctamente
            imei_length = int(received[:4], 16)
            self.imei = bytes.fromhex(received[4:4+imei_length*2]).decode('ascii')
            logging.info(f"Device authenticated | IMEI: {self.imei}")
            self.conn.send(b'\x01')
        else:
            logging.warning("Authentication failed: insufficient data received")
            self.conn.send(b'\x00')
            raise Exception("Authentication failed")

    def handle_data(self):
        logging.info("Waiting for GPS data...")

        try:
            buff = self.conn.recv(8192)
            received = binascii.hexlify(buff).decode()
            logging.debug(f"Received GPS data: {received}")

            if len(received) > 8:  # Asegurarse de que hay al menos algunos datos
                decoder = Decoder(payload=received, imei=self.imei)
                records = decoder.decode_data()

                if records:
                    self.data_manager.save_data(self.imei, records)
                    self.display_records(records)
                    self.conn.send(struct.pack("!L", len(records)))
                    logging.info(f"Processed {len(records)} records from IMEI: {self.imei}")
                else:
                    logging.warning("No valid records decoded from the GPS data")
                    self.conn.send(struct.pack("!L", 0))
            else:
                logging.warning("No valid GPS data received")
                self.conn.send(struct.pack("!L", 0))
        except Exception as e:
            logging.error(f"Error handling data: {e}")
            self.conn.send(struct.pack("!L", 0))

    def display_records(self, records):
        for i, record in enumerate(records, 1):
            print(f"\n--- GPS Record {i} ---")
            print(json.dumps(record, indent=2))
            print("------------------")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_server():
    if is_port_in_use(PORT):
        logging.error(f"Port {PORT} is already in use. Please choose a different port.")
        return

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        logging.info(f"Server started successfully on {HOST}:{PORT}")
        print(f"Server is running on {HOST}:{PORT}")
        print("Waiting for GPS connections...")

        while True:
            conn, addr = server.accept()
            ClientThread(conn, addr).start()
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    finally:
        server.close()
        logging.info("Server shut down")

if __name__ == "__main__":
    print("Starting GPS Server...")
    print("Press Ctrl+C to stop the server")
    start_server()