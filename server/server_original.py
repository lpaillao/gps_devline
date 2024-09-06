import socket
from threading import Thread
from datetime import datetime
import struct
import binascii
import json
import os
import logging
import sys
import time
import pickle

# Global Variables
HOST = '0.0.0.0'
PORT = 6006
DATA_DIR = 'gps_data'

# Set up logging
logging.basicConfig(level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("gps_server.log"),
                        logging.StreamHandler(sys.stdout)
                    ])

class Decoder:
    def __init__(self, payload, imei):
        self.payload = payload
        self.imei = imei
        self.precision = 10000000.0

    def decode_data(self) -> int:
        logging.debug(f"Raw payload: {self.payload}")

        number_of_rec = int(self.payload[18:20], 16)
        number_of_rec_end = int(self.payload[len(self.payload)-10:-8], 16)
        logging.info(f"Number of records: {number_of_rec}, End number: {number_of_rec_end}")

        avl_data = self.payload[20:-10]
        logging.debug(f"AVL data: {avl_data}")

        records = []
        if number_of_rec == number_of_rec_end:
            position = 0
            for _ in range(number_of_rec):
                timestamp_hex = avl_data[position:position+16]
                timestamp_int = int(timestamp_hex, 16)
                timestamp = datetime.utcfromtimestamp(timestamp_int/1e3)
                position += 16

                priority = int(avl_data[position:position+2], 16)
                position += 2

                longitude = int(avl_data[position:position+8], 16) / self.precision
                position += 8

                latitude = int(avl_data[position:position+8], 16) / self.precision
                position += 8

                altitude = int(avl_data[position:position+4], 16)
                position += 4
                altitude = int(avl_data[position:position+4], 16)
                position += 4

                angle = int(avl_data[position:position+4], 16)
                position += 4

                satellites = int(avl_data[position:position+2], 16)
                position += 2

                speed = int(avl_data[position:position+4], 16)
                position += 4

                io_event_code = int(avl_data[position:position + 2], 16)
                position += 2

                number_of_io_elements = int(avl_data[position:position + 2], 16)
                position += 2

                io_data = {}
                for bit_size in [1, 2, 4, 8]:
                    num_elements = int(avl_data[position:position + 2], 16)
                    position += 2
                    for _ in range(num_elements):
                        io_code = int(avl_data[position:position + 2], 16)
                        position += 2
                        io_val = int(avl_data[position:position + 2 * bit_size], 16)
                        position += 2 * bit_size
                        io_data[io_code] = io_val

                record = {
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
                    "I/O Event Code": io_event_code,
                    "Number of I/O Elements": number_of_io_elements,
                    "I/O Data": io_data
                }
                records.append(record)
                logging.info(f"Decoded record: {json.dumps(record, indent=2)}")

        else:
            logging.warning(f"Number of records mismatch: start={number_of_rec}, end={number_of_rec_end}")

        return records

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
        received = binascii.hexlify(buff)
        logging.debug(f"Received authentication data: {received}")
        if len(received) > 2:
            self.imei = received.decode()
            logging.info(f"Device authenticated | IMEI: {self.imei}")
            self.conn.send(b'\x01')
        else:
            logging.warning("Authentication failed: insufficient data received")
            self.conn.send(b'\x00')
            raise Exception("Authentication failed")

    def handle_data(self):
        logging.info("Waiting for GPS data...")
        buff = self.conn.recv(8192)
        received = binascii.hexlify(buff)
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