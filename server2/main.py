import logging
from server import start_server
from config import setup_logging

if __name__ == "__main__":
    setup_logging()
    logging.info("Starting GPS Server...")
    print("Starting GPS Server...")
    print("Press Ctrl+C to stop the server")
    start_server()