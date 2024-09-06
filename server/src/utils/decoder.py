import logging
from datetime import datetime

class Decoder:
    def __init__(self, payload, imei):
        self.payload = payload
        self.imei = imei
        self.precision = 10000000.0

    def decode_data(self):
        logging.debug(f"Raw payload: {self.payload}")

        if len(self.payload) < 32:  # Minimum length for a valid payload
            logging.warning("Payload too short")
            return []

        data_field_length = int(self.payload[8:16], 16)
        codec = int(self.payload[16:18], 16)
        number_of_data = int(self.payload[18:20], 16)

        logging.info(f"Data field length: {data_field_length}, Codec: {codec}, Number of data: {number_of_data}")

        avl_data = self.payload[20:-4]  # Exclude CRC at the end
        records = []

        position = 0
        for _ in range(number_of_data):
            if len(avl_data) - position < 64:  # Minimum length for a single record
                logging.warning("Insufficient data for record")
                break

            timestamp = int(avl_data[position:position+16], 16)
            position += 16

            priority = int(avl_data[position:position+2], 16)
            position += 2

            longitude = int(avl_data[position:position+8], 16) / self.precision
            position += 8

            latitude = int(avl_data[position:position+8], 16) / self.precision
            position += 8

            altitude = int(avl_data[position:position+4], 16)
            position += 4

            angle = int(avl_data[position:position+4], 16)
            position += 4

            satellites = int(avl_data[position:position+2], 16)
            position += 2

            speed = int(avl_data[position:position+4], 16)
            position += 4

            event_io_id = int(avl_data[position:position+2], 16)
            position += 2

            total_io = int(avl_data[position:position+2], 16)
            position += 2

            io_data = {}
            for bit_size in [1, 2, 4, 8]:
                num_elements = int(avl_data[position:position+2], 16)
                position += 2
                for _ in range(num_elements):
                    if len(avl_data) - position < 2 + (2 * bit_size):
                        logging.warning("Insufficient data for IO element")
                        break
                    io_id = int(avl_data[position:position+2], 16)
                    position += 2
                    io_value = int(avl_data[position:position + 2 * bit_size], 16)
                    position += 2 * bit_size
                    io_data[io_id] = io_value

            record = {
                "IMEI": self.imei,
                "DateTime": datetime.utcfromtimestamp(timestamp // 1000).isoformat(),
                "Priority": priority,
                "GPS Data": {
                    "Longitude": longitude,
                    "Latitude": latitude,
                    "Altitude": altitude,
                    "Angle": angle,
                    "Satellites": satellites,
                    "Speed": speed,
                },
                "Event IO ID": event_io_id,
                "Total IO Elements": total_io,
                "IO Data": io_data
            }
            records.append(record)
            logging.info(f"Decoded record: {record}")

        if len(records) != number_of_data:
            logging.warning(f"Number of decoded records ({len(records)}) does not match expected number ({number_of_data})")

        return records