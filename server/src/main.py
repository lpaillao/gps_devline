import asyncio
import sys
from pathlib import Path

# Añadir el directorio raíz al PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from src.gps_handler import GPSHandler
from src.data_manager import DataManager
from src.api.routes import setup_routes
from config.settings import MONGODB_URL, GPS_PORT, API_PORT
import logging

# Configuración de logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("gps_server.log"),
                        logging.StreamHandler(sys.stdout)
                    ])

app = FastAPI()

async def start_gps_server(gps_handler):
    server = await asyncio.start_server(
        gps_handler.handle_connection, '0.0.0.0', GPS_PORT
    )
    logging.info(f"GPS server running on port {GPS_PORT}")
    async with server:
        await server.serve_forever()

async def main():
    # Conexión a MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.gps_database

    # Inicializar componentes
    data_manager = DataManager(db)
    gps_handler = GPSHandler(data_manager)

    # Configurar rutas de la API
    setup_routes(app, data_manager)

    # Iniciar el servidor GPS en un proceso separado
    gps_server_task = asyncio.create_task(start_gps_server(gps_handler))

    # Iniciar el servidor de la API
    import uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=API_PORT, log_level="info")
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    finally:
        gps_server_task.cancel()
        await client.close()

if __name__ == '__main__':
    logging.info("Starting GPS Server...")
    logging.info("Press Ctrl+C to stop the server")
    asyncio.run(main())