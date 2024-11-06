import numpy as np
import logging
from config.database_connector import database_connector
from repository.log_repository import LogRepository
from repository.report_repository import ReportRepository
from data_processing import (remove_idle_data, remove_209_and_non_increasing_x, 
                             median_filter, define_cycle, regression, 
                             fuel_calculation, calculate_total_distance,
                             calculate_operating_time)
from model.report_data import FuelCycleCreate
from datetime import datetime
import prisma.errors import UniqueViolationError

log_cycle = logging.getLogger("Log Cycle")
log_hour = logging.getLogger("Log Hour")

class EfficiencyService:
    
    @staticmethod
    async def cycle_efficiency():
        async with database_connector.prisma.tx() as ts:
            data_vehicles = await LogRepository.get_all_data()
            for vehicle in data_vehicles:
                try:
                    vehicle_id = vehicle["vehicle_id"]
                    log_cycle.info(f"[Cycle] Mengambil data mentah untuk vehicle_id: {vehicle_id}")
                    
                    # Mengambil total_distance terbaru dari fuel_report_hour berdasarkan vehicle_id
                    recent_total_distance = await ReportRepository.get_recent_total_distance(vehicle_id)
                    
                    # Ambil data yang belum diproses untuk setiap vehicle_id
                    data = await LogRepository.get_unprocessed_cycle(vehicle_id)
                    if data:
                        np_timestamp = np.array([entry["timestamp"] for entry in data])
                        np_latitude = np.array([entry["latitude"] for entry in data])
                        np_longitude = np.array([entry["longitude"] for entry in data])
                        np_fuel = np.array([entry["fuel"] for entry in data])
                        np_operating_status = np.array([entry["operate_status"] for entry in data])

                        # Kalkulasi np_distance dari latitude dan longitude
                        coordinates = list(map(list, zip(np_latitude, np_longitude)))
                        np_distance = calculate_total_distance(recent_total_distance, coordinates)

                        dt_array = np.column_stack((np_timestamp, np_distance, np_fuel, np_operating_status))
                        adjusted_data = remove_idle_data(dt_array)

                        if adjusted_data.size > 0:
                            x = adjusted_data[:, 1]
                            y = adjusted_data[:, 2]
                            
                            x_filtered, y_filtered = remove_209_and_non_increasing_x(x, y)
                            y_median = median_filter(y_filtered)
                            data_cycle = define_cycle(x_filtered, y_median)
                            data_reg = regression(data_cycle)
                            final_data = fuel_calculation(dt_array, data_reg)

                            if (y_median[-693:] - y_median[-694] >= 16).any():
                                for row in final_data[:-1]:
                                    try:
                                        res_fuel_cycle = FuelCycleCreate(
                                            distance=float(row[0]),
                                            fuel=float(row[1]),
                                            fuel_efficiency=float(row[2]),
                                            timestamp_first=datetime.strptime(row[3], '%Y-%m-%dT%H:%M:%SZ'),
                                            timestamp_last=datetime.strptime(row[4], '%Y-%m-%dT%H:%M:%SZ'),
                                            vehicle={"connect": {"id": vehicle_id}}
                                        )
                                        # Create ke fuel_cycle
                                        await ReportRepository.create_cycle(res_fuel_cycle, ts)
                                        # Update status calculation_cycle_status di data_teltonika_buffer
                                        await LogRepository.update_cycle_status(vehicle_id, row[4], ts)
                                        log_cycle.info(f"[Data Created] Vehicle ID: {vehicle_id}, Efficiency: {row[2]}, Timestamp_last: {row[4]}")
                                    except UniqueViolationError as uniq_err:
                                        log_cycle.info(f"Data untuk Vehicle ID: {vehicle_id} dan Timestamp_last: {row[4]} sudah ada. Info: {uniq_err}")
                                    except Exception as err:
                                        log_cycle.error(f"Error saat membuat data baru. Vehicle ID: {vehicle_id}, Error: {err}")
                            else:
                                log_cycle.info("Data belum memenuhi siklus sepenuhnya")
                        else:
                            log_cycle.info(f"Data untuk id {vehicle_id}, tidak tersedia")
                except Exception as e:
                    log_cycle.error(f"Error proses Cycle, vehicle_id: {vehicle_id}, Error: {e}")
                    continue


    @staticmethod
    async def hour_efficiency():
        async with database_connector.prisma.tx() as ts:
            data_vehicle = await LogRepository.get_all_data()
            for vehicle in data_vehicle:
                try:
                    vehicle_id = vehicle["vehicle_id"]
                    log_hour.info(f"[Cycle] Mengambil data mentah untuk vehicle_id: {vehicle_id}")
                    # Mengambil total_distance terbaru dari fuel_report_hour berdasarkan vehicle_id
                    recent_total_distance = await ReportRepository.get_recent_total_distance(vehicle_id)

                    data = await LogRepository.get_unprocessed_hour(vehicle_id)
                    if data:
                        np_fuel = np.array([entry["fuel"] for entry in data])
                        np_latitude = np.array([entry["latitude"] for entry in data])
                        np_longitude = np.array([entry["longitude"] for entry in data])
                        np_operating_status = np.array([entry["operate_status"] for entry in data])

                        # Kalkulasi np_distance dari latitude dan longitude
                        coordinates = list(map(list, zip(np_latitude, np_longitude)))
                        np_distance = calculate_total_distance(recent_total_distance, coordinates)
                        np_timestamp = np.array([entry["timestamp"] for entry in data])

                        dt_array = np.column_stack((np_fuel, np_distance, np_timestamp, np_operating_status))

                        # Mengambil data siklus dari fuel_cycle
                        data_cycle_efficiency = await ReportRepository.get_cycle_efficiency(vehicle_id)
                        if data_cycle_efficiency:
                            cycle_efficiency = np.array([entry["fuel_efficiency"] for entry in data_cycle_efficiency])
                            timestamp_first = np.array([entry["timestamp_first"] for entry in data_cycle_efficiency])
                            timestamp_last = np.array([entry["timestamp_last"] for entry in data_cycle_efficiency])
                        
                        # Menghitung total operating time
                        operating_time = calculate_operating_time(dt_array)



                except Exception as e:
                    log_hour.error(f"Error proses Cycle, vehicle_id: {vehicle_id}, Error: {e}")