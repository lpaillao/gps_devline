import struct
from datetime import datetime, timezone
import logging

class Decoder:
    def __init__(self, payload, imei):
        self.payload = payload
        self.imei = imei
        self.index = 0

    def decode_data(self):
        try:
            self.index = 8  # Skip first 8 bytes (4 zeros + 4 data length)
            codec_id = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2

            if codec_id != 0x08:
                raise ValueError(f"Unsupported codec ID: {codec_id}")

            num_of_data = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2

            records = []
            for _ in range(num_of_data):
                record = self.parse_avl_record()
                if record:
                    records.append(record)

            return records
        except Exception as e:
            logging.error(f"Error decoding data: {e}")
            return None

    def parse_avl_record(self):
        try:
            timestamp = struct.unpack('>Q', bytes.fromhex(self.payload[self.index:self.index + 16]))[0]
            timestamp = datetime.fromtimestamp(timestamp / 1000, timezone.utc)
            self.index += 16

            priority = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2

            longitude = struct.unpack('>i', bytes.fromhex(self.payload[self.index:self.index + 8]))[0] / 10000000.0
            self.index += 8
            latitude = struct.unpack('>i', bytes.fromhex(self.payload[self.index:self.index + 8]))[0] / 10000000.0
            self.index += 8
            altitude = struct.unpack('>H', bytes.fromhex(self.payload[self.index:self.index + 4]))[0]
            self.index += 4
            angle = struct.unpack('>H', bytes.fromhex(self.payload[self.index:self.index + 4]))[0]
            self.index += 4
            satellites = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2
            speed = struct.unpack('>H', bytes.fromhex(self.payload[self.index:self.index + 4]))[0]
            self.index += 4

            io_records = self.parse_io_data()

            return {
                "IMEI": self.imei,
                "DateTime": timestamp.isoformat(),
                "Priority": priority,
                "Location": {
                    "Longitude": longitude,
                    "Latitude": latitude,
                    "Altitude": altitude,
                    "Angle": angle,
                    "Satellites": satellites,
                    "Speed": speed,
                },
                "I/O Data": io_records
            }
        except Exception as e:
            logging.error(f"Error parsing AVL record: {e}")
            return None

    def parse_io_data(self):
        io_records = {}
        try:
            event_io_id = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2
            io_records['Event IO ID'] = event_io_id

            n_total_id = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2

            for io_size in [1, 2, 4, 8]:
                n_items = int(self.payload[self.index:self.index + 2], 16)
                self.index += 2
                for _ in range(n_items):
                    io_id = int(self.payload[self.index:self.index + 2], 16)
                    self.index += 2
                    io_value = struct.unpack(f'>{"BHIQ"[io_size // 2]}', bytes.fromhex(self.payload[self.index:self.index + io_size * 2]))[0]
                    self.index += io_size * 2
                    io_records[f'IO ID {io_id}'] = io_value

            return io_records
        except Exception as e:
            logging.error(f"Error parsing IO data: {e}")
            return io_records