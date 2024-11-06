from prisma import Prisma
from config.database_connector import database_connector
from model.report_data import VehicleCreate, FuelCycleCreate, FuelHourCreate

class ReportRepository:
    @staticmethod
    async def create_vehicle(data: VehicleCreate, db = database_connector.prisma):
        return await db.vehicle.create(data)

    @staticmethod
    async def create_cycle(data: FuelCycleCreate, db = database_connector.prisma):
        return await db.cycle_efficiency.create(data)
    
    @staticmethod
    async def create_hour(data: FuelHourCreate, db = database_connector.prisma):
        return await db.hour_efficiency.create(data)
