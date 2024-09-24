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

            # Skip preamble and data length
            self.index = 16  # 8 bytes for preamble, 8 bytes for data length
            
            # Parse the codec ID (next 1 byte)
            codec_id = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2

            if codec_id != 0x08:
                raise ValueError(f"Unsupported codec ID: {codec_id}")

            # Parse the number of data records (next 1 byte)
            num_of_data = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2

            records = []
            for _ in range(num_of_data):
                record = self.parse_avl_record()
                records.append(record)

            # Verify number of records at the end
            num_of_data_end = int(self.payload[-4:-2], 16)
            if num_of_data != num_of_data_end:
                logging.warning(f"Number of records mismatch: start={num_of_data}, end={num_of_data_end}")

            return records

        except Exception as e:
            logging.error(f"Error decoding data: {e}")
            return None

    def parse_avl_record(self):
        # Parse the timestamp (next 8 bytes)
        timestamp = struct.unpack('>Q', bytes.fromhex(self.payload[self.index:self.index + 16]))[0]
        timestamp = datetime.fromtimestamp(timestamp / 1000, timezone.utc)
        self.index += 16

        # Parse the priority (next 1 byte)
        priority = int(self.payload[self.index:self.index + 2], 16)
        self.index += 2

        # Parse GPS data
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

        # Parse IO data
        io_records = self.parse_io_data()

        return {
            "IMEI": self.imei,
            "DateTime": timestamp.isoformat(),
            "Priority": priority,
            "GPS Data": {
                "Longitude": longitude,
                "Latitude": latitude,
                "Altitude": altitude,
                "Angle": angle,
                "Satellites": satellites,
                "Speed": speed,
            },
            "I/O Data": io_records
        }

    def parse_io_data(self):
        io_records = {}

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
            self.imei = received
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

            if len(received) > 2:
                decoder = Decoder(payload=received, imei=self.imei)
                records = decoder.decode_data()

                if records:
                    self.data_manager.save_data(self.imei, records)
                    self.display_records(records)
                    self.conn.send(struct.pack("!L", len(records)))
                    logging.info(f"Processed {len(records)} records from IMEI: {self.imei}")
                else:
                    logging.warning("No valid records decoded from the GPS data")
                    self.conn.send(b'\x00')
            else:
                logging.warning("No valid GPS data received")
                self.conn.send(b'\x00')
        except Exception as e:
            logging.error(f"Error handling data: {e}")
            self.conn.send(b'\x00')

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