from prisma import Prisma
from config.database_connector import database_connector
from model.log_data import FuelLog
from datetime import datetime, timedelta


class LogRepository:

    @staticmethod
    async def get_all_vehicle_id(db=database_connector.prisma):
        data = await db.vehicle.find_many()
        return [val.id for val in data]

    @staticmethod
    async def get_all_cycle_id(db=database_connector.prisma):
        data = await db.fuel_cycle.find_many()
        return [val.id for val in data]

    @staticmethod
    async def update_cycle_status(vehicle_id, timestamp_last, db=database_connector.prisma):
        # Update semua entri `data_teltonika_buffer` dengan timestamp <= timestamp_last menjadi `True`
        await db.data_teltonika_buffer.update_many(
            where={"vehicle_id": vehicle_id,"timestamp": {"lte": timestamp_last}},
            data={"calculation_cycle_status": True}
        )

    @staticmethod
    async def update_hour_status(vehicle_id, end_time: datetime, db=database_connector.prisma):
        one_hour = timedelta(hours=1)
        # Update semua entri `data_teltonika_buffer` dengan timestamp <= end_time menjadi `True`
        await db.data_teltonika_buffer.update_many(
            where={"vehicle_id": vehicle_id,"timestamp": {"lte": end_time+one_hour}},
            data={"calculation_hour_status": True}
        )

    @staticmethod
    async def get_all_data(db=database_connector.prisma):
        # Mengambil semua data dari data_teltonika_buffer, termasuk relasi vehicle
        data = await db.data_teltonika_buffer.find_many(include={"vehicle": True}) # Menyertakan relasi vehicle untuk mendapatkan vehicle_id
        return data
    
    @staticmethod
    async def get_unprocessed_data(vehicle_id, db=database_connector.prisma):
        data = await db.data_teltonika_buffer.find_many(
            where={"vehicle_id": vehicle_id, "calculation_cycle_status": False, "calculation_hour_status": False},
            include={"vehicle": True},
        )
        return data

    @staticmethod
    async def get_unprocessed_cycle(vehicle_id, db=database_connector.prisma):
        data = await db.data_teltonika_buffer.find_many(
            where={"vehicle_id": vehicle_id, 
            "calculation_cycle_status": False}, 
            include={"vehicle": True}
        )
        return data

    @staticmethod
    async def get_unprocessed_hour(vehicle_id, start_time: datetime, end_time: datetime, db=database_connector.prisma):
        data = await db.data_teltonika_buffer.find_many(
            where={"vehicle_id": vehicle_id,
                "calculation_hour_status": False,
                "timestamp": {
                    "gte": start_time,  # Greater than or equal to start_time
                    "lt": end_time      # Less than end_time
                }
            },
            include={"vehicle": True}
        )
        return data