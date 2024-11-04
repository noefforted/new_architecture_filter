from prisma import Prisma
from config.database_connector import database_connector
from model.fuel_cycle import FuelCycleCreate
from model.hour_report import FuelHourCreate

class FuelEfficiencyRepository:
    @staticmethod
    async def create_cycle(data: FuelCycleCreate, db = database_connector.prisma):
        return await db.cycle_efficiency.create(data)
    
    @staticmethod
    async def create_hour(data: FuelHourCreate, db = database_connector.prisma):
        return await db.hour_efficiency.create(data)
