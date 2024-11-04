from prisma import Prisma
from config.database_connector import database_connector
from model.timescale_data import FuelTimescale

class TimescaleRepository:
    @staticmethod
    async def get_all_data(db = database_connector.prisma):
        data = await db.fuel_data.find_many()
        return [val["imei"] for val in data]
    
    async def get_unprocessed_cycle(db = database_connector.prisma):
        data = await db.fuel_data.find_first(where={"calculation_cycle_status": False})
        if data is None:
            return None
        return FuelTimescale(
            imei=data["imei"],
            timestamp=data["timestamp"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            altitude=data["altitude"],
            heading=data["heading"],
            voltage=data["voltage"],
            speed=data["speed"],
            distance_total=data["distance_total"],
            fuel=data["fuel"],
            power_status=data["power_status"],
            operating_status=data["operating_status"],
            device_status=data["device_status"],
            calculation_cycle_status=data["calculation_cycle_status"],
            calculation_hour_status=data["calculation_hour_status"],
            expired_date=data["expired_date"]
        )
    
    async def get_unprocessed_hour(db = database_connector.prisma):
        data = await db.fuel_data.find_first(where={"calculation_hour_status": False})
        if data is None:
            return None
        return FuelTimescale(
            imei=data["imei"],
            timestamp=data["timestamp"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            altitude=data["altitude"],
            heading=data["heading"],
            voltage=data["voltage"],
            speed=data["speed"],
            distance_total=data["distance_total"],
            fuel=data["fuel"],
            power_status=data["power_status"],
            operating_status=data["operating_status"],
            device_status=data["device_status"],
            calculation_cycle_status=data["calculation_cycle_status"],
            calculation_hour_status=data["calculation_hour_status"],
            expired_date=data["expired_date"]
        )
    
    async def get_unprocessed_data(db = database_connector.prisma):
        data = await db.fuel_data.find_first(where={"calculation_cycle_status": False, "calculation_hour_status": False})
        if data is None:
            return None
        return FuelTimescale(
            imei=data["imei"],
            timestamp=data["timestamp"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            altitude=data["altitude"],
            heading=data["heading"],
            voltage=data["voltage"],
            speed=data["speed"],
            distance_total=data["distance_total"],
            fuel=data["fuel"],
            power_status=data["power_status"],
            operating_status=data["operating_status"],
            device_status=data["device_status"],
            calculation_cycle_status=data["calculation_cycle_status"],
            calculation_hour_status=data["calculation_hour_status"],
            expired_date=data["expired_date"]
        )