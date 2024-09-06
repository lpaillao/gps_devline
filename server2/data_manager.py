import os
import json
import logging
from config import DATA_DIR

class DataManager:
    def __init__(self):
        self.ensure_data_dir()

    def ensure_data_dir(self):
        if not os.path.exists(DATA_DIR):
            try:
                os.makedirs(DATA_DIR)
                logging.info(f"Created data directory: {DATA_DIR}")
            except Exception as e:
                logging.error(f"Failed to create data directory: {e}")
                raise

    def save_data(self, imei, records):
        filename = os.path.join(DATA_DIR, f"{imei}.json")
        mode = 'a' if os.path.exists(filename) else 'w'
        try:
            with open(filename, mode) as f:
                json.dump(records, f, indent=2)
                f.write('\n')  # Add a newline for readability between records
            logging.info(f"Saved {len(records)} records for IMEI {imei}")
        except Exception as e:
            logging.error(f"Failed to save data for IMEI {imei}: {e}")