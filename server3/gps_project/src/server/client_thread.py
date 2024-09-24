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
        print(f"\n{'='*50}")
        print(f"Decoded GPS Data for IMEI: {self.imei}")
        print(f"{'='*50}")
        for i, record in enumerate(records, 1):
            print(f"\nRecord {i}:")
            print(f"  Timestamp: {record['DateTime']}")
            print(f"  Priority: {record['Priority']}")
            print("  Location:")
            print(f"    Latitude:  {record['Location']['Latitude']}")
            print(f"    Longitude: {record['Location']['Longitude']}")
            print(f"    Altitude:  {record['Location']['Altitude']} m")
            print(f"    Angle:     {record['Location']['Angle']}°")
            print(f"    Satellites:{record['Location']['Satellites']}")
            print(f"    Speed:     {record['Location']['Speed']} km/h")
            print("  I/O Data:")
            for key, value in record['I/O Data'].items():
                print(f"    {key}: {value}")
            if 'Fleet Data' in record:
                print("  Fleet Data:")
                for key, value in record['Fleet Data'].items():
                    print(f"    {key}: {value}")
            if 'Alerts' in record:
                print("  Alerts:")
                for alert in record['Alerts']:
                    print(f"    - {alert}")
        print(f"\n{'='*50}\n")