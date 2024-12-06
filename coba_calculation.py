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
from model.request_controller import ResponsePacketRecentReportHour
from datetime import datetime, timedelta, timezone
from prisma.errors import UniqueViolationError

from util.log import log_begin
log_begin()
log_cycle = logging.getLogger("Log Cycle")
log_hour = logging.getLogger("Log Hour")
log_recent_hour = logging.getLogger("Log Recent Hour")

class EfficiencyService:

    @staticmethod
    async def cycle_efficiency(db=database_connector.prisma):
        await database_connector.connect()
        vehicles = await db.vehicle.find_many()
        vehicle_ids = [val.id for val in vehicles]
        for vehicle_id in vehicle_ids:
            try:
                if vehicle_id is None:
                    log_cycle.error("Vehicle ID tidak ditemukan atau None")
                    continue

                batch_size = 50000
                while True:
                    recent_total_distance = await ReportRepository.get_recent_total_distance(vehicle_id)
                    data = await LogRepository.get_unprocessed_cycle(vehicle_id, batch_size, 0)
                    
                    if not data:
                        log_cycle.info(f"No data available for Vehicle ID: {vehicle_id} at date: {data[0].timestamp}")
                        break

                    log_cycle.info(f"[Cycle] Mengambil data mentah Vehicle ID: {vehicle_id} | Mulai tanggal: {data[0].timestamp} sampai: {data[-1].timestamp} | Length: {len(data)}")
                    np_timestamp = np.array([item.timestamp.timestamp() for item in data], dtype=np.float64)
                    np_latitude = np.array([item.latitude for item in data], dtype=np.float64)
                    np_longitude = np.array([item.longitude for item in data], dtype=np.float64)
                    np_fuel = np.array([item.fuel_level for item in data], dtype=np.float64)
                    np_operating_status = np.array([item.operate_status for item in data], dtype=np.int8)

                    coordinates = list(zip(np_latitude, np_longitude))
                    np_distance = calculate_total_distance(recent_total_distance, coordinates)

                    # Gunakan np_distance tanpa mengubah ke timedelta
                    dt_array = np.column_stack((np_timestamp, np_distance, np_fuel, np_operating_status))
                    adjusted_data = remove_idle_data(dt_array)

                    if adjusted_data.size > 0:
                        x = adjusted_data[:, 1]
                        y = adjusted_data[:, 2]
                        
                        x_filtered, y_filtered = remove_209_and_non_increasing_x(x, y)
                        y_median = median_filter(y_filtered)
                        data_cycle = define_cycle(x_filtered, y_median)
                        data_reg = regression(data_cycle)
                        final_data = fuel_cycle_calculation(dt_array, data_reg)
                        if len(final_data)<2:
                            log_cycle.error(f"Data belum siklus penuh Vehicle ID: {vehicle_id}")
                            break
                        for row in final_data[:-1]:
                            try:
                                res_fuel_cycle = FuelCycleCreate(
                                    fuel=float(row[0]),
                                    distance=float(row[1]),
                                    fuel_level_first=float(row[2]),
                                    fuel_efficiency=float(row[3]),
                                    timestamp_first=datetime.strptime(row[4], '%Y-%m-%dT%H:%M:%SZ'),
                                    timestamp_last=datetime.strptime(row[5], '%Y-%m-%dT%H:%M:%SZ'),
                                    vehicle={"connect": {"id": vehicle_id}}
                                )
                                await ReportRepository.create_fuel_cycle(res_fuel_cycle)
                                log_cycle.info(f"[Data Created] Vehicle ID: {vehicle_id}, Efficiency: {row[3]}, Timestamp_last: {row[5]}")
                                # Update calculation_cycle_status yang sudah diproses
                                await LogRepository.update_cycle_status(vehicle_id, row[5])
                                log_cycle.info(f"Last Cycle Status Updated: {row[5]}")   
                            except UniqueViolationError as uniqerr:
                                log_cycle.error(f"Data duplicate Vehicle ID: {vehicle_id}, Timestamp_last: {row[5]}, tidak dibuat ulang ({uniqerr})")
                            except Exception as err:
                                log_cycle.error(f"Error saat membuat data baru. Vehicle ID: {vehicle_id}, Error: {err}")     
 
            except Exception as e:
                log_cycle.error(f"[Cycle] Error processing vehicle_id {vehicle_id}: {e}")
        await database_connector.disconnect()

    @staticmethod     
    async def hour_efficiency(db=database_connector.prisma):
        await database_connector.connect()
        vehicles = await db.vehicle.find_many()
        vehicle_ids = [val.id for val in vehicles]
        for ids in vehicle_ids:
            try:
                if ids is None:
                    log_cycle.error("Vehicle ID tidak ditemukan atau None")
                    continue
                    
                data_cycle_efficiency = await ReportRepository.get_cycle_efficiency(ids)

                for i in range(len(data_cycle_efficiency)):
                    recent_total_distance = await ReportRepository.get_recent_total_distance(ids)

                    cumulative_distance_hour = []
                    final_data_list = []

                    cycle_id = data_cycle_efficiency[i].id
                    vehicle_id = data_cycle_efficiency[i].vehicle.id
                    cycle_efficiency = data_cycle_efficiency[i].fuel_efficiency
                    fuel_level_first = data_cycle_efficiency[i].fuel_level_first
                    timestamp_first = data_cycle_efficiency[i].timestamp_first
                    if i < len(data_cycle_efficiency) - 1:
                        timestamp_first_next = data_cycle_efficiency[i+1].timestamp_first
                    else:
                        timestamp_first_next = datetime.now(timezone.utc)
                    if cycle_efficiency == 0:
                        log_hour.error(f"[Hour] Cycle efficiency is zero for Vehicle ID: {vehicle_id}, Cycle ID: {cycle_id}")
                        continue

                    log_hour.info(f"[Hour] Mengambil data mentah Vehicle ID: {vehicle_id} dan Cycle ID: {cycle_id}")  

                    current_time = timestamp_first
                    while current_time <= timestamp_first_next:
                        next_time = current_time + timedelta(hours=1)
                        data = await LogRepository.get_unprocessed_hour(vehicle_id, current_time, next_time)

                        if not data:
                            final_data_list.append([0, 0, 0, 0, 0, 0, 0, current_time, 3600, 0])
                            cumulative_distance_hour.append(0)
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
                        distance_1_hour = abs(distance_inside_hour[-1] - distance_inside_hour[0])
                        cumulative_distance_hour.append(distance_1_hour)

                        arr_time_opstatus = np.column_stack((np_timestamp, np_operating_status))

                        fuel_1_hour = (distance_1_hour / 1000) / cycle_efficiency

                        fuel_level_first_next = fuel_level_first - fuel_1_hour
                        operating_time_1_hour = calculate_operating_time_hour(arr_time_opstatus)

                        last_latitude = np_latitude[-1]
                        last_longitude = np_longitude[-1]
                        last_altitude = np_altitude[-1]
                        last_angle = np_angle[-1]

                        # Simpan data dalam list sementara
                        final_data_list.append([
                            fuel_1_hour, fuel_level_first, last_latitude, last_longitude, last_altitude, 
                            last_angle, distance_1_hour, current_time, 3600, operating_time_1_hour
                        ])
                        # Update current_time untuk iterasi berikutnya
                        fuel_level_first = np.maximum(fuel_level_first_next, 0)
                        current_time = next_time

                    # Hitung total_distance setelah loop selesai
                    total_distance = np.cumsum(cumulative_distance_hour)
                    total_distance_recent = total_distance + recent_total_distance
                    # print(f"Total Distance: {total_distance_recent}")

                    # Gabungkan data akhir ke dalam array `final_data`
                    final_data = np.array([
                        row + [total_distance_recent[i]]
                        for i, row in enumerate(final_data_list)
                    ])
                    for row in final_data:
                        try:
                            res_fuel_report_hour = FuelHourCreate(
                                fuel=float(row[0]),
                                fuel_level=float(row[1]),
                                latitude=float(row[2]),
                                longitude=float(row[3]),
                                altitude=float(row[4]),
                                angle=float(row[5]),
                                distance=float(row[6]),
                                total_distance=float(row[10]),
                                timestamp=row[7].replace(minute=0, second=0, microsecond=0),
                                sampling_time=int(row[8]),
                                operating_time=int(row[9]),
                                fuel_cycle={"connect": {"id": cycle_id}},
                                vehicle={"connect": {"id": vehicle_id}}
                            )
                            await ReportRepository.create_fuel_report_hour(res_fuel_report_hour)
                            log_hour.info(f"[Data Created] Vehicle ID: {vehicle_id}, Cycle ID: {cycle_id}, Timestamp: {row[7]}, Distance: {row[6]}")
                            # Update calculation_hour_status yang sudah diproses
                            await LogRepository.update_hour_status(vehicle_id, row[7])
                        except UniqueViolationError as uniqerr:
                            log_hour.error(f"Data duplicate Vehicle ID: {vehicle_id}, Cycle ID: {cycle_id}, Timestamp: {row[7]}, tidak dibuat ulang ({uniqerr})")
                        except Exception as err:
                            log_hour.error(f"Error saat membuat data baru. Vehicle ID: {vehicle_id}, Error: {err}")

            except Exception as e:
                log_hour.error(f"[Hour] Error processing vehicle_id: {ids}, {e}")
        await database_connector.disconnect()

import asyncio
asyncio.run(EfficiencyService.cycle_efficiency())
asyncio.run(EfficiencyService.hour_efficiency())