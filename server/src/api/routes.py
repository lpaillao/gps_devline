from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter()

def setup_routes(app, data_manager):
    @router.get("/gps")
    async def get_connected_gps():
        return data_manager.get_connected_gps()

    @router.get("/gps/{imei}")
    async def get_gps_data(imei: str):
        data = data_manager.get_latest_data(imei)
        if not data:
            raise HTTPException(status_code=404, detail="GPS not found or not connected")
        return data

    @router.get("/gps/{imei}/history")
    async def get_gps_history(imei: str, start_time: datetime, end_time: datetime):
        history = await data_manager.get_gps_history(imei, start_time, end_time)
        return history

    app.include_router(router, prefix="/api/v1")