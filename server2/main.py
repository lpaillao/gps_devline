import logging
from server import start_server
from api import start_api
from config import setup_logging
import threading

if __name__ == "__main__":
    setup_logging()
    logging.info("Starting GPS Server and API...")
    print("Starting GPS Server and API...")
    print("Press Ctrl+C to stop the server")
    
    api_thread = threading.Thread(target=start_api)
    api_thread.start()
    
    start_server()