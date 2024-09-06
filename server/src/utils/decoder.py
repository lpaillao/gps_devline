import asyncio
import binascii
import struct
from src.utils.decoder import Decoder
import logging

class GPSHandler:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    async def handle_connection(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logging.info(f"New connection from {addr}")

        try:
            imei = await self.handle_authentication(reader, writer)
            if not imei:
                return

            while True:
                await self.handle_gps_data(imei, reader, writer)

        except asyncio.CancelledError:
            logging.info(f"Connection handler for {addr} was cancelled")
        except Exception as e:
            logging.error(f"Error handling connection from {addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            await self.data_manager.disconnect_gps(imei)
            logging.info(f"Connection closed for {addr}")

    async def handle_authentication(self, reader, writer):
        logging.info("Waiting for device authentication...")
        imei_data = await reader.read(17)  # IMEI is typically 15 digits, plus 2 bytes for length
        if len(imei_data) < 2:
            logging.warning("Authentication failed: insufficient data received")
            writer.write(b'\x00')
            await writer.drain()
            return None

        imei_length = imei_data[0]
        imei = imei_data[1:1+imei_length].decode()
        logging.info(f"Device authenticated | IMEI: {imei}")
        writer.write(b'\x01')
        await writer.drain()
        return imei

    async def handle_gps_data(self, imei, reader, writer):
        logging.info("Waiting for GPS data...")
        header = await reader.read(8)
        if len(header) != 8:
            logging.warning("Invalid GPS data header")
            return

        data_length = struct.unpack(">I", header[4:])[0]
        data = await reader.read(data_length)
        
        if len(data) != data_length:
            logging.warning(f"Incomplete GPS data received. Expected {data_length}, got {len(data)}")
            return

        hex_data = binascii.hexlify(header + data).decode()
        logging.debug(f"Received GPS data: {hex_data}")

        decoder = Decoder(payload=hex_data, imei=imei)
        records = decoder.decode_data()

        if records:
            await self.data_manager.store_gps_data(imei, records)
            self.display_records(records)
            response = struct.pack(">I", len(records))
            writer.write(response)
            await writer.drain()
            logging.info(f"Processed {len(records)} records from IMEI: {imei}")
        else:
            logging.warning("No valid records decoded from the GPS data")
            writer.write(struct.pack(">I", 0))
            await writer.drain()

    def display_records(self, records):
        for i, record in enumerate(records, 1):
            print(f"\n--- GPS Record {i} ---")
            print(record)
            print("------------------")