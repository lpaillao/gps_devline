# server2/client_handler.py
from threading import Thread
import binascii
import struct
import logging
import json
from decoder import Decoder
from data_manager import DataManager
from utils import format_gps_data, format_io_data
from gps_manager import GPSManager

class ClientHandler(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.imei = "desconocido"
        self.data_manager = DataManager()
        self.gps_manager = GPSManager()

    def run(self):
        logging.info(f"Nueva conexión desde {self.addr}")
        try:
            self.handle_authentication()
            self.gps_manager.connect(self.imei)
            while True:
                if not self.handle_data():
                    break
        except Exception as e:
            logging.error(f"Error al manejar el cliente {self.addr}: {e}")
        finally:
            self.gps_manager.disconnect(self.imei)
            self.conn.close()
            logging.info(f"Conexión cerrada para {self.addr}")

    def handle_authentication(self):
        logging.info("Esperando autenticación del dispositivo...")
        try:
            buff = self.conn.recv(8192)
            received = binascii.hexlify(buff)
            logging.debug(f"Datos de autenticación recibidos: {received}")
            if len(received) > 2:
                self.imei = received.decode()
                logging.info(f"Dispositivo autenticado | IMEI: {self.imei}")
                self.conn.send(b'\x01')
            else:
                raise ValueError("Datos de autenticación insuficientes")
        except Exception as e:
            logging.error(f"Error durante la autenticación: {e}")
            self.conn.send(b'\x00')
            raise

    def handle_data(self):
        logging.info("Esperando datos GPS...")
        try:
            buff = self.conn.recv(8192)
            if not buff:
                logging.info("Conexión cerrada por el cliente")
                return False
            
            received = binascii.hexlify(buff)
            logging.debug(f"Datos GPS recibidos: {received}")
            
            if len(received) > 2:
                decoder = Decoder(carga_util=received, imei=self.imei)
                records = decoder.decodificar_datos()
                if records:
                    self.data_manager.guardar_datos(self.imei, records)
                    self.display_records(records)
                    self.conn.send(struct.pack("!L", len(records)))
                    logging.info(f"Procesados {len(records)} registros del IMEI: {self.imei}")
                else:
                    logging.warning("No se decodificaron registros válidos de los datos GPS")
                    self.conn.send(struct.pack("!L", 0))
            else:
                logging.warning("No se recibieron datos GPS válidos")
                self.conn.send(struct.pack("!L", 0))
            
            return True
        except Exception as e:
            logging.error(f"Error al manejar datos GPS: {e}")
            return False

    def display_records(self, records):
        for i, record in enumerate(records, 1):
            print(f"\n{'='*40}")
            print(f"Registro GPS {i} - IMEI: {record['IMEI']}")
            print(f"{'='*40}")
            print(f"Marca de tiempo: {record['DateTime']}")
            print(f"Prioridad: {record['Priority']}")
            print("\nDatos GPS:")
            print(format_gps_data(record['GPS Data']))
            print("\nDatos de E/S:")
            print(format_io_data({
                'Código de Evento E/S': record['I/O Event Code'],
                'Número de Elementos E/S': record['Number of I/O Elements'],
                'Elementos E/S': record['I/O Data']
            }))
            print(f"{'='*40}\n")