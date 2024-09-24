# server2/main.py
import logging
from server import start_server
from api import start_api
from config import setup_logging
import threading

if __name__ == "__main__":
    setup_logging()
    logging.info("Iniciando Servidor GPS y API...")
    print("Iniciando Servidor GPS y API...")
    print("Presione Ctrl+C para detener el servidor")
    api_thread = threading.Thread(target=start_api)
    api_thread.start()
    
    start_server()