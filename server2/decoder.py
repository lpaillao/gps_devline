from datetime import datetime
import logging

class Decoder:
    def __init__(self, payload, imei):
        self.payload = payload
        self.imei = imei
        self.precision = 10000000.0

    def decode_data(self):
        logging.debug(f"Raw payload: {self.payload}")

        number_of_rec = int(self.payload[18:20], 16)
        number_of_rec_end = int(self.payload[len(self.payload)-10:-8], 16)
        logging.info(f"Number of records: {number_of_rec}, End number: {number_of_rec_end}")

        avl_data = self.payload[20:-10]
        logging.debug(f"AVL data: {avl_data}")

        records = []
        if number_of_rec == number_of_rec_end:
            position = 0
            for _ in range(number_of_rec):
                record = self._decode_single_record(avl_data[position:])
                records.append(record)
                position += self._get_record_length(avl_data[position:])
                logging.info(f"Decoded record: {record}")
        else:
            logging.warning(f"Number of records mismatch: start={number_of_rec}, end={number_of_rec_end}")

        return records

    def _decode_single_record(self, record_data):
        timestamp = self._decode_timestamp(record_data[0:16])
        priority = int(record_data[16:18], 16)
        gps_data = self._decode_gps_data(record_data[18:46])
        io_data = self._decode_io_data(record_data[46:])

        return {
            "IMEI": self.imei,
            "DateTime": timestamp.isoformat(),
            "Priority": priority,
            "GPS Data": gps_data,
            "I/O Data": io_data
        }

    def _decode_timestamp(self, timestamp_hex):
        timestamp_int = int(timestamp_hex, 16)
        return datetime.utcfromtimestamp(timestamp_int/1000)

    def _decode_gps_data(self, gps_data):
        return {
            "Longitude": int(gps_data[0:8], 16) / self.precision,
            "Latitude": int(gps_data[8:16], 16) / self.precision,
            "Altitude": int(gps_data[16:20], 16),
            "Angle": int(gps_data[20:24], 16),
            "Satellites": int(gps_data[24:26], 16),
            "Speed": int(gps_data[26:28], 16)
        }

    def _decode_io_data(self, io_data):
        position = 0
        io_event_code = int(io_data[position:position+2], 16)
        position += 2

        number_of_io_elements = int(io_data[position:position+2], 16)
        position += 2

        io_elements = {}
        for bit_size in [1, 2, 4, 8]:
            num_elements = int(io_data[position:position+2], 16)
            position += 2
            for _ in range(num_elements):
                io_code = int(io_data[position:position+2], 16)
                position += 2
                io_val = int(io_data[position:position+2*bit_size], 16)
                position += 2 * bit_size
                io_elements[io_code] = io_val

        return {
            "I/O Event Code": io_event_code,
            "Number of I/O Elements": number_of_io_elements,
            "I/O Elements": io_elements
        }

    def _get_record_length(self, record_data):
        # A single record consists of:
        # 8 bytes (timestamp) + 1 byte (priority) + 14 bytes (GPS data) + variable IO data
        io_data_start = 23
        io_event_elements = int(record_data[io_data_start+2:io_data_start+4], 16)
        io_data_length = 4  # IO event code (1 byte) + Number of IO elements (1 byte)
        
        position = io_data_start + 4
        for bit_size in [1, 2, 4, 8]:
            num_elements = int(record_data[position:position+2], 16)
            position += 2
            io_data_length += 2 + num_elements * (1 + bit_size)

        return io_data_start + io_data_length