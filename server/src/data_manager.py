from datetime import datetime
import logging

class DataManager:
    def __init__(self, db):
        self.db = db
        self.connected_gps = set()
        self.latest_data = {}

    async def store_gps_data(self, imei, records):
        self.latest_data[imei] = records[-1]  # Store the most recent record
        self.connected_gps.add(imei)

        for record in records:
            await self.db.gps_history.insert_one({
                "imei": imei,
                "timestamp": datetime.utcnow(),
                "data": record
            })
        logging.info(f"Saved {len(records)} records for IMEI {imei}")

    async def disconnect_gps(self, imei):
        self.connected_gps.discard(imei)
        self.latest_data.pop(imei, None)
        logging.info(f"Disconnected GPS with IMEI: {imei}")

    def get_connected_gps(self):
        return list(self.connected_gps)

    def get_latest_data(self, imei):
        return self.latest_data.get(imei)

    async def get_gps_history(self, imei, start_time, end_time):
        cursor = self.db.gps_history.find({
            "imei": imei,
            "timestamp": {"$gte": start_time, "$lte": end_time}
        }).sort("timestamp", 1)
        return await cursor.to_list(length=None)