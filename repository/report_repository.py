from prisma import Prisma
from config.database_connector import database_connector
from model.report_data import VehicleCreate, FuelCycleCreate, FuelHourCreate
from datetime import datetime, timedelta

class ReportRepository:

    @staticmethod
    async def get_recent_total_distance(vehicle_id, db=database_connector.prisma):
        # Mengambil total_distance terbaru berdasarkan vehicle_id
        data = await db.fuel_report_hour.find_first(
            where={"vehicle_id": vehicle_id},
            order={"timestamp": "desc"},
            select={"total_distance": True}
        )
        # Mengembalikan `total_distance` terbaru, atau 0 jika data tidak ditemukan
        return data["total_distance"] if data else 0

    @staticmethod
    async def get_cycle_efficiency(vehicle_id, db=database_connector.prisma):
        time_24_hours_ago = datetime.utcnow() - timedelta(hours=24)
        data = await db.fuel_cycle.find_many(
            where={
                "vehicle_id": vehicle_id,
                "timestamp_last": {"gte": time_24_hours_ago}  # Filter untuk 24 jam terakhir
            },
            select={
                "fuel_efficiency": True,  # Mengambil hanya kolom fuel_efficiency
                "timestamp_first": True    # Opsional, untuk referensi waktu
                "timestamp_last": True    # Opsional, untuk referensi waktu
            }
        )
        return data

    @staticmethod
    async def create_vehicle(data: VehicleCreate, db=database_connector.prisma):
        return await db.vehicle.create(data)

    @staticmethod
    async def create_cycle(data: FuelCycleCreate, db=database_connector.prisma):
        return await db.fuel_cycle.create(data)

    @staticmethod
    async def create_hour(data: FuelHourCreate, db=database_connector.prisma):
        return await db.fuel_report_hour.create(data)
