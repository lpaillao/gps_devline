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
            logging.debug(f"Payload length: {len(self.payload)}")
            logging.debug(f"Raw payload: {self.payload}")

            if len(self.payload) < 16:
                logging.error(f"Payload too short: {len(self.payload)} bytes")
                return None

            self.index = 16  # Skip first 16 characters (8 bytes: 4 zeros + 4 data length)
            logging.debug(f"Starting decoding from index: {self.index}")

            if self.index + 2 > len(self.payload):
                logging.error("Payload too short to read codec ID")
                return None

            codec_id = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2
            logging.debug(f"Codec ID: {codec_id}")

            if codec_id != 0x08:
                logging.error(f"Unsupported codec ID: {codec_id}")
                return None

            if self.index + 2 > len(self.payload):
                logging.error("Payload too short to read number of data")
                return None

            num_of_data = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2
            logging.debug(f"Number of data records: {num_of_data}")

            records = []
            for i in range(num_of_data):
                logging.debug(f"Parsing record {i+1}/{num_of_data}")
                record = self.parse_avl_record()
                if record:
                    records.append(record)
                else:
                    logging.warning(f"Failed to parse record {i+1}")

            logging.info(f"Successfully parsed {len(records)} out of {num_of_data} records")
            return records
        except Exception as e:
            logging.exception(f"Error decoding data: {e}")
            return None

    def parse_avl_record(self):
        try:
            if self.index + 16 > len(self.payload):
                logging.error("Payload too short to read timestamp")
                return None

            timestamp = struct.unpack('>Q', bytes.fromhex(self.payload[self.index:self.index + 16]))[0]
            timestamp = datetime.fromtimestamp(timestamp / 1000, timezone.utc)
            self.index += 16
            logging.debug(f"Timestamp: {timestamp}")

            if self.index + 2 > len(self.payload):
                logging.error("Payload too short to read priority")
                return None

            priority = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2
            logging.debug(f"Priority: {priority}")

            if self.index + 24 > len(self.payload):
                logging.error("Payload too short to read GPS data")
                return None

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

            logging.debug(f"GPS Data: Lon={longitude}, Lat={latitude}, Alt={altitude}, Angle={angle}, Sat={satellites}, Speed={speed}")

            io_records = self.parse_io_data()

            record = {
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

            # Añadir Fleet Data si está disponible
            fleet_data = self.process_fleet_data(record)
            if fleet_data:
                record['Fleet Data'] = fleet_data

            # Añadir Alerts si están disponibles
            alerts = self.check_for_alerts(record)
            if alerts:
                record['Alerts'] = alerts

            return record
        except Exception as e:
            logging.exception(f"Error parsing AVL record: {e}")
            return None

    def parse_io_data(self):
        io_records = {}
        try:
            if self.index + 2 > len(self.payload):
                logging.error("Payload too short to read Event IO ID")
                return io_records

            event_io_id = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2
            io_records['Event IO ID'] = event_io_id
            logging.debug(f"Event IO ID: {event_io_id}")

            if self.index + 2 > len(self.payload):
                logging.error("Payload too short to read N of Total IO")
                return io_records

            n_total_id = int(self.payload[self.index:self.index + 2], 16)
            self.index += 2
            logging.debug(f"N of Total IO: {n_total_id}")

            for io_size in [1, 2, 4, 8]:
                if self.index + 2 > len(self.payload):
                    logging.error(f"Payload too short to read N of IO for size {io_size}")
                    break

                n_items = int(self.payload[self.index:self.index + 2], 16)
                self.index += 2
                logging.debug(f"N of IO for size {io_size}: {n_items}")

                for _ in range(n_items):
                    if self.index + 2 > len(self.payload):
                        logging.error(f"Payload too short to read IO ID for size {io_size}")
                        break

                    io_id = int(self.payload[self.index:self.index + 2], 16)
                    self.index += 2

                    if self.index + io_size * 2 > len(self.payload):
                        logging.error(f"Payload too short to read IO value for size {io_size}")
                        break

                    io_value = struct.unpack(f'>{"BHIQ"[io_size // 2]}', bytes.fromhex(self.payload[self.index:self.index + io_size * 2]))[0]
                    self.index += io_size * 2
                    io_records[f'IO ID {io_id}'] = io_value
                    logging.debug(f"IO ID {io_id}: {io_value}")

            return io_records
        except Exception as e:
            logging.exception(f"Error parsing IO data: {e}")
            return io_records