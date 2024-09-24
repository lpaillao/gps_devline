import logging
import binascii
import struct
from threading import Thread
from src.decoder.gps_decoder import Decoder
from src.data.data_manager import DataManager

class ClientThread(Thread):
    def __init__(self, client_socket, address):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.address = address
        self.imei = None
        self.data_manager = DataManager()

    def run(self):
        try:
            self.handle_authentication()
            self.handle_data()
        except Exception as e:
            logging.error(f"Error handling client {self.address}: {e}")
        finally:
            self.client_socket.close()
            if self.imei:
                self.data_manager.remove_connected_gps(self.imei)
            logging.info(f"Connection closed for {self.address}")

    def handle_authentication(self):
        buff = self.client_socket.recv(17)  # 2 bytes length + 15 bytes IMEI
        if len(buff) < 17:
            raise ValueError("Insufficient data for authentication")

        imei_hex = buff.hex()
        imei_length = int(imei_hex[:4], 16)
        self.imei = bytes.fromhex(imei_hex[4:4+imei_length*2]).decode('ascii')
        logging.info(f"Device authenticated | IMEI: {self.imei}")
        self.client_socket.send(b'\x01')
        self.data_manager.add_connected_gps(self.imei)

    def handle_data(self):
        while True:
            try:
                length_bytes = self.client_socket.recv(4)
                if len(length_bytes) != 4:
                    break

                data_length = struct.unpack('>I', length_bytes)[0]
                data = self.client_socket.recv(data_length)
                if len(data) != data_length:
                    break

                received = binascii.hexlify(length_bytes + data).decode()
                decoder = Decoder(payload=received, imei=self.imei)
                records = decoder.decode_data()

                if records:
                    self.data_manager.save_gps_data(self.imei, records)
                    self.client_socket.send(struct.pack(">I", len(records)))
                    logging.info(f"Processed {len(records)} records from IMEI: {self.imei}")
                else:
                    self.client_socket.send(struct.pack(">I", 0))
            except Exception as e:
                logging.error(f"Error processing data from {self.imei}: {e}")
                break