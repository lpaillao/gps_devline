import logging
import sys

HOST = '0.0.0.0'
PORT = 6006
DATA_DIR = 'gps_data'

def setup_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("gps_server.log"),
                            logging.StreamHandler(sys.stdout)
                        ])