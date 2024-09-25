import logging
from server.gps_server import start_server
from api.api import start_api

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("gps_tracking.log"),
                            logging.StreamHandler()
                        ])
    
    print("Starting GPS Tracking System...")
    print("Press Ctrl+C to stop the server")
    
    # Start the GPS server in a separate thread
    from threading import Thread
    server_thread = Thread(target=start_server)
    server_thread.start()
    
    # Start the API server
    start_api()