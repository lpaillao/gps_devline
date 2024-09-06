from datetime import datetime

class DataManager:
    def __init__(self, db):
        self.db = db
        self.connected_gps = set()
        self.latest_data = {}

    async def store_gps_data(self, imei, data):
        self.latest_data[imei] = data
        self.connected_gps.add(imei)

        await self.db.gps_history.insert_one({
            "imei": imei,
            "timestamp": datetime.utcnow(),
            "data": data
        })

    async def disconnect_gps(self, imei):
        self.connected_gps.discard(imei)
        self.latest_data.pop(imei, None)

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