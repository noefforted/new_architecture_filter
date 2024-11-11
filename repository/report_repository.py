from config.database_connector import database_connector
from model.report_data import VehicleCreate, FuelCycleCreate, FuelHourCreate
from model.request_controller import ResponsePacketRecentReportHour
from datetime import datetime, timedelta
import asyncio
from asyncio import StreamReader, StreamWriter

class ReportRepository:

    @staticmethod
    async def get_recent_total_distance(vehicle_id, db=database_connector.prisma):
        # Mengambil total_distance terbaru berdasarkan vehicle_id
        data = await db.fuel_report_hour.find_first(
            where={"vehicle_id": vehicle_id},
            order={"timestamp": "desc"},
            include={"vehicle": True}
        )
        # Mengembalikan `total_distance` terbaru, atau 0 jika data tidak ditemukan
        return data["total_distance"] if data else 0

    @staticmethod
    async def get_cycle_efficiency(db=database_connector.prisma):
        # Ambil timestamp terawal dari data_teltonika_buffer dengan calculation_hour_status = true, termasuk vehicle untuk mendapatkan vehicle_id
        data_teltonika_records = await db.data_teltonika_buffer.find_many(
            where={"calculation_hour_status": False},
            include={"vehicle": True},
            order={"timestamp": "asc"}  # Urutkan untuk mendapatkan timestamp paling awal
        )
        # Pastikan ada data yang memenuhi kriteria
        if not data_teltonika_records:
            return []
        # Ambil timestamp paling awal dan daftar unique vehicle_id
        earliest_timestamp = data_teltonika_records[0].timestamp
        vehicle_ids = list({record.vehicle.id for record in data_teltonika_records if record.vehicle})
        # Query fuel_cycle berdasarkan vehicle_id dan filter timestamp_first
        data = await db.fuel_cycle.find_many(
            where={"vehicle": {"id": {"in": vehicle_ids}},"timestamp_first": {"gte": earliest_timestamp}},  # Filter timestamp_first sesuai kriteria
            include={"vehicle": True}
        )
        return data

    @staticmethod
    async def get_cycle_by_vehicle_id(vehicle_id, db=database_connector.prisma):
        # Ambil timestamp terawal dari data_teltonika_buffer dengan calculation_hour_status = true, termasuk vehicle untuk mendapatkan vehicle_id
        data_teltonika_records = await db.data_teltonika_buffer.find_many(
            where={"calculation_hour_status": False},
            include={"vehicle": True},
            order={"timestamp": "asc"}  # Urutkan untuk mendapatkan timestamp paling awal
        )
        # Pastikan ada data yang memenuhi kriteria
        if not data_teltonika_records:
            return []
        # Ambil timestamp paling awal dan daftar unique vehicle_id
        earliest_timestamp = data_teltonika_records[0].timestamp

        data = await db.fuel_cycle.find_many(
            where={"vehicle_id": vehicle_id, "timestamp_first": {"gte": earliest_timestamp}},
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
    