import logging
import binascii
import struct
from threading import Thread
from utils.decoder import Decoder
from data.data_manager import DataManager

class ClientHandler(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.imei = "unknown"

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

            if len(received) > 8:
                decoder = Decoder(payload=received, imei=self.imei)
                records = decoder.decode_data()

                if records:
                    DataManager.save_data(self.imei, records)
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