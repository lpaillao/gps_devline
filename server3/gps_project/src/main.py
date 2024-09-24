import logging
from server.gps_server import GPSServer
from api.rest_api import start_rest_api
from config import CONFIG

def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename=CONFIG['log_file'],
                        filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def start_services():
    setup_logging()
    logging.info("Starting GPS Server...")
    gps_server = GPSServer(CONFIG['gps_host'], CONFIG['gps_port'])
    gps_server.start()

    logging.info("Starting REST API...")
    start_rest_api()

if __name__ == "__main__":
    start_services()