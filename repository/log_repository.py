from prisma import Prisma
from config.database_connector import database_connector
from model.log_data import FuelLog


class LogRepository:

    @staticmethod
    async def update_cycle_status(vehicle_id, timestamp_last, db=database_connector.prisma):
        # Update semua entri `data_teltonika_buffer` dengan timestamp <= timestamp_last menjadi `True`
        await db.data_teltonika_buffer.update_many(
            where={
                "vehicle_id": vehicle_id,
                "timestamp": {"lte": timestamp_last}
            },
            data={"calculation_cycle_status": True}
        )

    @staticmethod
    async def get_all_data(db=database_connector.prisma):
        data = await db.data_teltonika_buffer.find_many()
        return data
    
    @staticmethod
    async def get_unprocessed_data(vehicle_id, db=database_connector.prisma):
        data = await db.data_teltonika_buffer.find_many(
            where={"vehicle_id": vehicle_id, "calculation_cycle_status": False, "calculation_hour_status": False},
            include={"vehicle": True},
        )
        return [
            {
                "fuel_log": FuelLog(
                    timestamp=item["timestamp"],
                    latitude=item["latitude"],
                    longitude=item["longitude"],
                    altitude=item["altitude"],
                    angle=item["angle"],
                    speed=item["speed"],
                    battery_voltage=item["battery_voltage"],
                    total_odometer=item["total_odometer"],
                    fuel=item["fuel"],
                    fuel_used_gps=item["fuel_used_gps"],
                    fuel_rate_gps=item["fuel_rate_gps"],
                    power_input=item["power_input"],
                    operate_status=item["operate_status"],
                    digital_input_2=item["digital_input_2"],
                    gsm_signal=item["gsm_signal"],
                    ignition_on_counter=item["ignition_on_counter"],
                    data_payload=item["data_payload"],
                    vehicle_id=item["vehicle_id"],
                    calculation_cycle_status=item["calculation_cycle_status"],
                    calculation_hour_status=item["calculation_hour_status"],
                ),
                "vehicle_data": item.vehicle,
            }
            for item in data
        ]

    @staticmethod
    async def get_unprocessed_cycle(vehicle_id, db=database_connector.prisma):
        data = await db.data_teltonika_buffer.find_many(
            where={"vehicle_id": vehicle_id, "calculation_cycle_status": False}, include={"vehicle": True}
        )
        return [
            {
                "fuel_log": FuelLog(
                    timestamp=item["timestamp"],
                    latitude=item["latitude"],
                    longitude=item["longitude"],
                    altitude=item["altitude"],
                    angle=item["angle"],
                    speed=item["speed"],
                    battery_voltage=item["battery_voltage"],
                    total_odometer=item["total_odometer"],
                    fuel=item["fuel"],
                    fuel_used_gps=item["fuel_used_gps"],
                    fuel_rate_gps=item["fuel_rate_gps"],
                    power_input=item["power_input"],
                    operate_status=item["operate_status"],
                    digital_input_2=item["digital_input_2"],
                    gsm_signal=item["gsm_signal"],
                    ignition_on_counter=item["ignition_on_counter"],
                    data_payload=item["data_payload"],
                    vehicle_id=item["vehicle_id"],
                    calculation_cycle_status=item["calculation_cycle_status"],
                    calculation_hour_status=item["calculation_hour_status"],
                ),
                "vehicle_data": item.vehicle,
            }
            for item in data
        ]

    @staticmethod
    async def get_unprocessed_hour(vehicle_id, db=database_connector.prisma):
        data = await db.data_teltonika_buffer.find_many(
            where={"vehicle_id": vehicle_id, "calculation_hour_status": False}, include={"vehicle": True}
        )
        return [
            {
                "fuel_log": FuelLog(
                    timestamp=item["timestamp"],
                    latitude=item["latitude"],
                    longitude=item["longitude"],
                    altitude=item["altitude"],
                    angle=item["angle"],
                    speed=item["speed"],
                    battery_voltage=item["battery_voltage"],
                    total_odometer=item["total_odometer"],
                    fuel=item["fuel"],
                    fuel_used_gps=item["fuel_used_gps"],
                    fuel_rate_gps=item["fuel_rate_gps"],
                    power_input=item["power_input"],
                    operate_status=item["operate_status"],
                    digital_input_2=item["digital_input_2"],
                    gsm_signal=item["gsm_signal"],
                    ignition_on_counter=item["ignition_on_counter"],
                    data_payload=item["data_payload"],
                    vehicle_id=item["vehicle_id"],
                    calculation_cycle_status=item["calculation_cycle_status"],
                    calculation_hour_status=item["calculation_hour_status"],
                ),
                "vehicle_data": item.vehicle,
            }
            for item in data
        ]
