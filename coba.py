import numpy as np
import logging
from config.database_connector import database_connector
from repository.log_repository import LogRepository
from repository.report_repository import ReportRepository
from service.data_processing import (remove_idle_data, remove_209_and_non_increasing_x, 
                             median_filter, define_cycle, regression, 
                             fuel_cycle_calculation, calculate_total_distance,
                             calculate_operating_time_hour)
from model.report_data import FuelCycleCreate, FuelHourCreate
from datetime import datetime, timedelta
import asyncio


log_cycle = logging.getLogger("Log Cycle")
log_hour = logging.getLogger("Log Hour")

@staticmethod     
async def hour_efficiency():
    await database_connector.connect()
    async with database_connector.prisma.tx() as ts:
        data_cycle_efficiency = await ReportRepository.get_cycle_efficiency()
        cumulative_distance_hour = []
        final_data_list = []

        for cycle in data_cycle_efficiency:
            cycle_id = cycle.id
            vehicle_id = cycle.vehicle.id
            cycle_efficiency = cycle.fuel_efficiency
            timestamp_first = cycle.timestamp_first
            timestamp_last = cycle.timestamp_last        

            current_time = timestamp_first
            while current_time < timestamp_last:
                next_time = current_time + timedelta(hours=1)
                data = await LogRepository.get_unprocessed_hour(vehicle_id, current_time, next_time)

                if not data:
                    current_time = next_time
                    continue

                # Ekstraksi data yang dibutuhkan untuk setiap entry dalam `data`
                np_timestamp = np.array([entry.timestamp.timestamp() for entry in data], dtype=np.float64)
                np_latitude = np.array([entry.latitude for entry in data], dtype=np.float64)
                np_longitude = np.array([entry.longitude for entry in data], dtype=np.float64)
                np_altitude = np.array([entry.altitude for entry in data], dtype=np.float64)
                np_angle = np.array([entry.angle for entry in data], dtype=np.float64)
                np_operating_status = np.array([entry.operate_status for entry in data], dtype=np.int8)
                
                coordinates = list(zip(np_latitude, np_longitude))
                distance_inside_hour = calculate_total_distance(0, coordinates)
                distance_1_hour = distance_inside_hour[-1] - distance_inside_hour[0]
                print(f"Distance 1 Hour: {distance_1_hour}")
                cumulative_distance_hour.append(distance_1_hour)

                arr_time_opstatus = np.column_stack((np_timestamp, np_operating_status))

                # Update current_time untuk iterasi berikutnya
                current_time = next_time

                fuel_1_hour = (distance_1_hour / 1000) / cycle_efficiency
                operating_time_1_hour = calculate_operating_time_hour(arr_time_opstatus)

                last_latitude = np_latitude[-1]
                last_longitude = np_longitude[-1]
                last_altitude = np_altitude[-1]
                last_angle = np_angle[-1]

                # Simpan data dalam list sementara
                final_data_list.append([
                    fuel_1_hour, last_latitude, last_longitude, last_altitude, 
                    last_angle, distance_1_hour, current_time, 3600, operating_time_1_hour
                ])

            # Hitung total_distance setelah loop selesai
            total_distance = np.cumsum(cumulative_distance_hour)

        # Gabungkan data akhir ke dalam array `final_data`
        final_data = np.array([
            row + [total_distance[i]]
            for i, row in enumerate(final_data_list)
        ])

        # print(f"Final Data: {final_data}")
        for row in final_data:
            try:
                res_fuel_report_hour = FuelHourCreate(
                    fuel=float(row[0]),
                    latitude=float(row[1]),
                    longitude=float(row[2]),
                    altitude=float(row[3]),
                    angle=float(row[4]),
                    distance=float(row[5]),
                    total_distance=float(row[9]),  # Sesuaikan dengan total_distance di kolom terakhir
                    timestamp=row[6],
                    sampling_time=int(row[7]),
                    operating_time=int(row[8]),
                    fuel_cycle={"connect": {"id": cycle_id}},
                    vehicle={"connect": {"id": vehicle_id}}
                )
                async with database_connector.prisma.tx() as ts:
                    await ReportRepository.create_fuel_report_hour(res_fuel_report_hour, ts)
                    await LogRepository.update_hour_status(vehicle_id, row[6], ts)
                log_hour.info(f"[Data Created] Vehicle ID: {vehicle_id}, Timestamp: {row[5]}")
            except Exception as err:
                log_hour.error(f"Error saat membuat data baru. Vehicle ID: {vehicle_id}, Error: {err}")

    await database_connector.disconnect()

asyncio.run(hour_efficiency())
