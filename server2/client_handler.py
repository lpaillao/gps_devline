from threading import Thread
import binascii
import struct
import logging
from decoder import Decoder
from data_manager import DataManager
from utils import format_gps_data, format_io_data

class ClientHandler(Thread):
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
                print(f"\n{'='*40}")
                print(f"GPS Record {i} - IMEI: {record['IMEI']}")
                print(f"{'='*40}")
                print(f"Timestamp: {record['DateTime']}")
                print(f"Priority: {record['Priority']}")
                
                print("\nGPS Data:")
                print(format_gps_data(record['GPS Data']))
                
                print("\nI/O Data:")
                print(format_io_data(record['I/O Data']))
                
                print(f"{'='*40}\n")