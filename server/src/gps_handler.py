import asyncio
from src.utils.decoder import Decoder

class GPSHandler:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    async def handle_connection(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"New connection from {addr}")

        try:
            imei = await self.authenticate(reader, writer)
            if not imei:
                print(f"Authentication failed for {addr}")
                return

            print(f"Authenticated device with IMEI: {imei}")
            await self.process_gps_data(imei, reader, writer)

        except asyncio.CancelledError:
            print(f"Connection handler for {addr} was cancelled")
        except Exception as e:
            print(f"Error handling connection from {addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            await self.data_manager.disconnect_gps(imei)
            print(f"Connection closed for {addr}")

    async def authenticate(self, reader, writer):
        # Implementación básica de autenticación
        writer.write(b"IMEI?\n")
        await writer.drain()
        imei = await reader.readline()
        imei = imei.decode().strip()
        if len(imei) == 15 and imei.isdigit():
            return imei
        return None

    async def process_gps_data(self, imei, reader, writer):
        while True:
            data = await reader.readline()
            if not data:
                break
            decoded_data = Decoder.decode(data)
            if decoded_data:
                await self.data_manager.store_gps_data(imei, decoded_data)
                writer.write(b"ACK\n")
                await writer.drain()