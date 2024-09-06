import asyncio
import binascii
from src.utils.decoder import Decoder
import logging
import struct

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
        auth_data = await reader.read(17)  # IMEI is typically 15 digits, plus 2 bytes for length
        if len(auth_data) < 2:
            logging.warning("Authentication failed: insufficient data received")
            writer.write(b'\x00')
            await writer.drain()
            return None

        imei_length = auth_data[0]
        imei = auth_data[1:1+imei_length].decode()
        logging.debug(f"Received authentication data: {imei}")
        logging.info(f"Device authenticated | IMEI: {imei}")
        writer.write(b'\x01')
        await writer.drain()
        return imei

    async def process_gps_data(self, imei, reader, writer):
        while True:
            try:
                header = await reader.read(8)
                if len(header) != 8:
                    logging.warning("Invalid GPS data header")
                    break

                data_length = struct.unpack(">I", header[4:])[0]
                data = await reader.read(data_length)
                
                if len(data) != data_length:
                    logging.warning(f"Incomplete GPS data received. Expected {data_length}, got {len(data)}")
                    continue

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
                    writer.write(struct.pack(">I", 0))  # Send 0 as response
                    await writer.drain()
            except Exception as e:
                logging.error(f"Error processing GPS data: {e}")
                break

    def display_records(self, records):
        for i, record in enumerate(records, 1):
            print(f"\n--- GPS Record {i} ---")
            print(record)
            print("------------------")