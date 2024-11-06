from prisma import Prisma
from config.database_connector import database_connector
from model.log_data import FuelLog

class LogRepository:
    @staticmethod
    async def get_all_data(db = database_connector.prisma):
        data = await db.fuel_data.find_many()
        return data
    
    async def get_unprocessed_cycle(db = database_connector.prisma):
        data = await db.fuel_data.find_first(where={"calculation_cycle_status": False})
        if data is None:
            return None
        return FuelLog(
            timestamp=data["timestamp"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            altitude=data["altitude"],
            angle=data["angle"],
            speed=data["speed"],
            battery_voltage=data["battery_voltage"],
            total_odometer=data["total_odometer"],
            fuel=data["fuel"],
            fuel_used_gps=data["fuel_used_gps"],
            fuel_rate_gps=data["fuel_rate_gps"],
            power_input=data["power_input"],
            operate_status=data["operate_status"],
            digital_input_2=data["digital_input_2"],
            gsm_signal=data["gsm_signal"],
            ignition_on_counter=data["ignition_on_counter"],
            data_payload=data["data_payload"],
            vehicle_id=data["vehicle_id"],
            calculation_cycle_status=data["calculation_cycle_status"],
            calculation_hour_status=data["calculation_hour_status"]
        )
    
    async def get_unprocessed_hour(db = database_connector.prisma):
        data = await db.fuel_data.find_first(where={"calculation_hour_status": False})
        if data is None:
            return None
        return FuelLog(
            timestamp=data["timestamp"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            altitude=data["altitude"],
            angle=data["angle"],
            speed=data["speed"],
            battery_voltage=data["battery_voltage"],
            total_odometer=data["total_odometer"],
            fuel=data["fuel"],
            fuel_used_gps=data["fuel_used_gps"],
            fuel_rate_gps=data["fuel_rate_gps"],
            power_input=data["power_input"],
            operate_status=data["operate_status"],
            digital_input_2=data["digital_input_2"],
            gsm_signal=data["gsm_signal"],
            ignition_on_counter=data["ignition_on_counter"],
            data_payload=data["data_payload"],
            vehicle_id=data["vehicle_id"],
            calculation_cycle_status=data["calculation_cycle_status"],
            calculation_hour_status=data["calculation_hour_status"]
        )
    
    async def get_unprocessed_data(db = database_connector.prisma):
        data = await db.fuel_data.find_first(where={"calculation_cycle_status": False, "calculation_hour_status": False})
        if data is None:
            return None
        return FuelLog(
            timestamp=data["timestamp"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            altitude=data["altitude"],
            angle=data["angle"],
            speed=data["speed"],
            battery_voltage=data["battery_voltage"],
            total_odometer=data["total_odometer"],
            fuel=data["fuel"],
            fuel_used_gps=data["fuel_used_gps"],
            fuel_rate_gps=data["fuel_rate_gps"],
            power_input=data["power_input"],
            operate_status=data["operate_status"],
            digital_input_2=data["digital_input_2"],
            gsm_signal=data["gsm_signal"],
            ignition_on_counter=data["ignition_on_counter"],
            data_payload=data["data_payload"],
            vehicle_id=data["vehicle_id"],
            calculation_cycle_status=data["calculation_cycle_status"],
            calculation_hour_status=data["calculation_hour_status"]
        )