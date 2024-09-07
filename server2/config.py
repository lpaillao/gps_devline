import logging
import sys
import os

HOST = '0.0.0.0'
PORT = 6006
DATA_DIR = 'gps_data'
DB_FILE = os.path.join(DATA_DIR, 'gps.db')

def setup_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("gps_server.log"),
                            logging.StreamHandler(sys.stdout)
                        ])