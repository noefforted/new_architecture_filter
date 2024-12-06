from config.database_connector import database_connector
from model.report_data import VehicleCreate, FuelCycleCreate, FuelHourCreate
from model.request_controller import ResponsePacketRecentReportHour
from datetime import datetime, timedelta
import asyncio
from asyncio import StreamReader, StreamWriter
from util.log import log_begin
# import logging
# log_begin()
# log_debug = logging.getLogger("Debug")

class ReportRepository:

    @staticmethod
    async def get_recent_total_distance(vehicle_id, db=database_connector.prisma):
        data = await db.fuel_report_hour.find_first(
            where={"vehicle_id": vehicle_id},
            order={"timestamp": "desc"},
            include={"vehicle": True}
        )
        return data.total_distance if data else 0

    @staticmethod
    async def get_cycle_efficiency(vehicle_id, db=database_connector.prisma):
        data_teltonika_records = await db.data_teltonika_buffer.find_first(
            where={"vehicle_id": vehicle_id, "calculation_hour_status": False},
            order={"timestamp": "asc"},
            include={"vehicle": True}
        )
        earliest_timestamp = data_teltonika_records.timestamp
        # log_debug.info(f"earliest_timestamp: {earliest_timestamp}")
        data = await db.fuel_cycle.find_many(
            where={"vehicle_id": vehicle_id, "timestamp_first": {"gte": earliest_timestamp}},
            include={"vehicle": True}
        )
        return data

    @staticmethod
    async def get_cycle_for_tcphour(vehicle_id, db=database_connector.prisma):
        data = await db.fuel_cycle.find_first(
            where={"vehicle_id": vehicle_id},
            order={"timestamp_last": "desc"}, 
            include={"vehicle": True}
        )
        return data
    
    @staticmethod
    async def create_vehicle(data: VehicleCreate, db=database_connector.prisma):
        return await db.vehicle.create(data)

    @staticmethod
    async def create_fuel_cycle(data: FuelCycleCreate, db=database_connector.prisma):
        return await db.fuel_cycle.create(data)

    @staticmethod
    async def create_fuel_report_hour(data: FuelHourCreate, db=database_connector.prisma):
        return await db.fuel_report_hour.create(data)
    