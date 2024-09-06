import asyncio
import binascii
from src.utils.decoder import Decoder
import logging

class GPSHandler:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    async def handle_connection(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logging.info(f"New connection from {addr}")

        try:
            imei = await self.authenticate(reader, writer)
            if not imei:
                logging.warning(f"Authentication failed for {addr}")
                return

            logging.info(f"Authenticated device with IMEI: {imei}")
            await self.process_gps_data(imei, reader, writer)

        except asyncio.CancelledError:
            logging.info(f"Connection handler for {addr} was cancelled")
        except Exception as e:
            logging.error(f"Error handling connection from {addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            await self.data_manager.disconnect_gps(imei)
            logging.info(f"Connection closed for {addr}")

    async def authenticate(self, reader, writer):
        writer.write(b'\x01')
        await writer.drain()
        imei_data = await reader.read(1024)
        imei = binascii.hexlify(imei_data).decode()
        if len(imei) > 2:
            logging.info(f"Device authenticated | IMEI: {imei}")
            return imei
        return None

    async def process_gps_data(self, imei, reader, writer):
        while True:
            data = await reader.read(1024)
            if not data:
                break
            hex_data = binascii.hexlify(data).decode()
            logging.debug(f"Received data: {hex_data}")
            
            decoder = Decoder(payload=hex_data, imei=imei)
            records = decoder.decode_data()
            if records:
                await self.data_manager.store_gps_data(imei, records)
                self.display_records(records)
                response = len(records).to_bytes(4, byteorder='big')
                writer.write(response)
                await writer.drain()
                logging.info(f"Processed {len(records)} records from IMEI: {imei}")
            else:
                logging.warning("No valid records decoded from the GPS data")
                writer.write(b'\x00')
                await writer.drain()

    def display_records(self, records):
        for i, record in enumerate(records, 1):
            logging.info(f"\n--- GPS Record {i} ---")
            logging.info(f"{record}")
            logging.info("------------------")