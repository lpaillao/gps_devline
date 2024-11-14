import logging
import binascii
import struct
import socket
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
        self.daemon = True
        self.is_running = True
        
        # Configuración de timeouts
        self.AUTH_TIMEOUT = 30  # segundos para autenticación
        self.DATA_TIMEOUT = 60  # segundos para datos GPS
        self.BUFFER_SIZE = 8192
        
    def run(self):
        """Método principal del thread"""
        logging.info(f"New connection from {self.addr}")
        try:
            # Establecer timeout para autenticación
            self.conn.settimeout(self.AUTH_TIMEOUT)
            self.handle_authentication()
            
            # Cambiar timeout para datos GPS
            self.conn.settimeout(self.DATA_TIMEOUT)
            
            while self.is_running:
                try:
                    if not self.handle_data():
                        break
                except socket.timeout:
                    logging.warning(f"Data reception timeout for IMEI: {self.imei}")
                    break
                except Exception as e:
                    logging.error(f"Error handling data: {e}")
                    break
                    
        except socket.timeout:
            logging.error(f"Authentication timeout for {self.addr}")
        except Exception as e:
            logging.error(f"Error handling client {self.addr}: {e}")
        finally:
            self.cleanup()

    def handle_authentication(self):
        """Maneja el proceso de autenticación del dispositivo"""
        logging.info("Waiting for device authentication...")
        
        try:
            # Recibir datos de autenticación
            buff = self.receive_with_retry(retries=3)
            if not buff:
                raise Exception("No authentication data received")
                
            received = binascii.hexlify(buff).decode()
            logging.debug(f"Received authentication data: {received}")
            
            # Validar y procesar datos de autenticación
            if len(received) > 2:
                imei_length = int(received[:4], 16)
                if len(received) < 4 + imei_length * 2:
                    raise Exception("Incomplete IMEI data received")
                    
                self.imei = bytes.fromhex(received[4:4+imei_length*2]).decode('ascii')
                
                # Validar formato IMEI
                if not self.validate_imei(self.imei):
                    raise Exception("Invalid IMEI format")
                    
                logging.info(f"Device authenticated | IMEI: {self.imei}")
                self.send_with_retry(b'\x01')
                return True
            else:
                raise Exception("Invalid authentication data format")
                
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            self.send_with_retry(b'\x00')
            raise

    def handle_data(self) -> bool:
        """
        Maneja la recepción y procesamiento de datos GPS
        
        Returns:
            bool: True si los datos se procesaron correctamente, False si debe cerrarse la conexión
        """
        try:
            buff = self.receive_with_retry(retries=2)
            if not buff:
                logging.info(f"Connection closed by client {self.imei}")
                return False
                
            received = binascii.hexlify(buff).decode()
            logging.debug(f"GPS data received: {received}")

            if len(received) > 8:
                return self.process_gps_data(received)
            else:
                logging.warning("Invalid GPS data received")
                self.send_with_retry(struct.pack("!L", 0))
                return True
                
        except Exception as e:
            logging.error(f"Error processing GPS data: {str(e)}")
            return False

    def process_gps_data(self, received: str) -> bool:
        """
        Procesa los datos GPS recibidos
        
        Args:
            received (str): Datos GPS en formato hexadecimal
            
        Returns:
            bool: True si los datos se procesaron correctamente
        """
        try:
            decoder = Decoder(payload=received, imei=self.imei)
            records = decoder.decode_data()

            if records:
                # Guardar datos
                DataManager.save_data(self.imei, records)
                
                # Enviar confirmación
                if not self.send_with_retry(struct.pack("!L", len(records))):
                    return False
                    
                logging.info(f"Processed {len(records)} records from IMEI: {self.imei}")
                
                # Emitir última ubicación
                try:
                    emit_gps_update(self.imei, records[-1])
                except Exception as e:
                    logging.error(f"Error emitting GPS update: {e}")
                    
                return True
            else:
                logging.warning("No valid records decoded")
                self.send_with_retry(struct.pack("!L", 0))
                return True
                
        except Exception as e:
            logging.error(f"Error processing GPS records: {str(e)}")
            return False

    def receive_with_retry(self, retries=3) -> bytes:
        """
        Recibe datos con reintentos
        
        Args:
            retries (int): Número de intentos
            
        Returns:
            bytes: Datos recibidos o None si falla
        """
        for attempt in range(retries):
            try:
                data = self.conn.recv(self.BUFFER_SIZE)
                if data:
                    return data
                return None
            except socket.timeout:
                if attempt == retries - 1:
                    raise
                logging.warning(f"Receive timeout, attempt {attempt + 1}/{retries}")
                continue
            except Exception as e:
                logging.error(f"Error receiving data: {str(e)}")
                raise

    def send_with_retry(self, data: bytes, retries=3) -> bool:
        """
        Envía datos con reintentos
        
        Args:
            data (bytes): Datos a enviar
            retries (int): Número de intentos
            
        Returns:
            bool: True si el envío fue exitoso
        """
        for attempt in range(retries):
            try:
                self.conn.send(data)
                return True
            except socket.timeout:
                if attempt == retries - 1:
                    return False
                logging.warning(f"Send timeout, attempt {attempt + 1}/{retries}")
                continue
            except Exception as e:
                logging.error(f"Error sending data: {str(e)}")
                return False

    def validate_imei(self, imei: str) -> bool:
        """
        Valida el formato del IMEI
        
        Args:
            imei (str): IMEI a validar
            
        Returns:
            bool: True si el formato es válido
        """
        # Implementar validación según tus requerimientos
        return len(imei) >= 10 and imei.isdigit()

    def cleanup(self):
        """Limpia los recursos del cliente"""
        self.is_running = False
        try:
            self.conn.close()
        except:
            pass
        logging.info(f"Connection closed for {self.addr}")