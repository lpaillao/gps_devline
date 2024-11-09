import logging
import binascii
import struct
from threading import Thread
from utils.decoder import Decoder
from data.data_manager import DataManager
from api.api import emit_gps_update

class ClientHandler(Thread):
    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.imei = "unknown"
        self.daemon = True  # Hacer que el hilo sea daemon por defecto

    def run(self):
        logging.info(f"New connection from {self.addr}")
        try:
            self.handle_authentication()
            while True:  # Bucle continuo para recibir datos
                try:
                    self.handle_data()
                except Exception as e:
                    logging.error(f"Error handling data: {e}")
                    break
        except Exception as e:
            logging.error(f"Error handling client {self.addr}: {e}")
        finally:
            try:
                self.conn.close()
            except:
                pass
            logging.info(f"Connection closed for {self.addr}")

    def handle_authentication(self):
        logging.info("Waiting for device authentication...")
        try:
            buff = self.conn.recv(8192)
            if not buff:  # Conexión cerrada por el cliente
                raise Exception("Connection closed during authentication")
                
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
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            try:
                self.conn.send(b'\x00')
            except:
                pass
            raise

    def handle_data(self):
        buff = self.conn.recv(8192)
        if not buff:  # Conexión cerrada por el cliente
            raise Exception("Connection closed by client")
            
        received = binascii.hexlify(buff).decode()
        logging.debug(f"Datos GPS recibidos: {received}")

        if len(received) > 8:
            decoder = Decoder(payload=received, imei=self.imei)
            records = decoder.decode_data()

            if records:
                DataManager.save_data(self.imei, records)
                self.conn.send(struct.pack("!L", len(records)))
                logging.info(f"Procesados {len(records)} registros del IMEI: {self.imei}")
                
                # Emitir la última ubicación
                latest_location = records[-1]
                try:
                    emit_gps_update(self.imei, latest_location)
                except Exception as e:
                    logging.error(f"Error emitting GPS update: {e}")
            else:
                logging.warning("No se decodificaron registros válidos")
                self.conn.send(struct.pack("!L", 0))
        else:
            logging.warning("Datos GPS inválidos recibidos")
            self.conn.send(struct.pack("!L", 0))