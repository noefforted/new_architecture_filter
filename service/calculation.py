import logging
from repository.log_repository import LogRepository
from config.database_connector import database_connector
import numpy as np
from data_processing import remove_idle_data, remove_209_and_non_increasing_x, median_filter, define_cycle, regression, fuel_calculation
from model.report_data import FuelCycleCreate
from datetime import datetime
from repository.report_repository import ReportRepository
import prisma.errors import UniqueViolationError

log_cycle = logging.getLogger("Log Cycle")
log_hour = logging.getLogger("Log Hour")

class EfficiencyService:
    
    @staticmethod
    async def cycle_efficiency():
        async with database_connector.prisma.tx() as ts:
            data_imei = await LogRepository.get_all_data()
            for imei in data_imei:
                try:
                    # Mengambil imei dari data yang belum di proses
                    log_cycle.info(f"[Cycle] Mengambil data mentah imei: {imei}")
                    data = await LogRepository.get_unprocessed_cycle(imei)
                    if data is not None:
                        np_timpestamp = np.array(data.timestamp)
                        np_distance = np.array(data.distance_total)
                        np_fuel = np.array(data.fuel)                 
                        np_power_status = np.array(data.power_status)
                        np_operating_status = np.array(data.operating_status)

                    dt_array = np.column_stack((np_timpestamp, np_distance, np_fuel, np_power_status, np_operating_status))
                    adjusted_data = remove_idle_data(dt_array)
                    
                    if len(adjusted_data) != 0:
                        x = adjusted_data[:, 1]
                        y = adjusted_data[:, 2]
                        
                        xbaru, ybaru = remove_209_and_non_increasing_x(x, y)
                        y_median = median_filter(ybaru)
                        data_cycle = define_cycle(xbaru, y_median)
                        data_reg = regression(data_cycle)

                        # Tidak perlu imei_array lagi, langsung menggunakan fuel_data_summary tanpa imei di dalam arraynya
                        final_data = fuel_calculation(dt_array, data_reg)

                        # bersar scanner terbaik imei 205 = 694, imei 237=897, imei 096=999, imei 323=
                        if (y_median[-693:] - y_median[-694] >= 16).any():
                            for row in final_data[:-1]:
                                try:
                                    res = FuelCycleCreate(
                                        imei=imei,  # IMEI masih disertakan di sini untuk logging
                                        total_fuel=float(row[0]),                 # fuel_consumed
                                        total_distance=float(row[1]),             # distance
                                        fuel_consumption=float(row[2]),           # fuel_rate
                                        timestamp_first=datetime.strptime(row[3], '%Y-%m-%dT%H:%M:%SZ'),  # time_initial
                                        timestamp_last=datetime.strptime(row[4], '%Y-%m-%dT%H:%M:%SZ'),    # time_terminal
                                    )
                                    # Menghubungkan ke database
                                    async with database_connector.prisma.tx() as ts:
                                        await ReportRepository.create_cycle(res, ts)
                                    log_cycle.info(f"[Data Created] Imei: {imei} Efficiency: {row[2]} Timestamp_last: {row[4]}")
                                except UniqueViolationError as uniq:
                                    log_cycle.info(f"Data dengan Imei: {imei} dan Timestamp_last: {row[4]} sudah ada, tidak akan dibuat ulang. Info: {uniq}")
                                except Exception as err:
                                    log_cycle.error(f"Error saat membuat data baru. Imei: {imei}, Error: {err}")
                        else:
                            log_cycle.info("Data belum memenuhi siklus sepenuhnya")
                    else:
                        log_cycle.info(f"Data untuk imei {imei}, tidak tersedia")
                except Exception as e:
                    log_cycle.error(f"imei: {imei} terjadi kesalahan: {e}")
                    continue                    



    @staticmethod
    async def hour_efficiency():
        try:
            async with database_connector.prisma.tx() as ts:
                data_imei = await LogRepository.get_all_data()
                for imei in data_imei:
                    # Mengambil imei dari data yang belum di proses
                    log_hour.info(f"[Hour] Mengambil data mentah imei: {imei}")
                    data = await LogRepository.get_unprocessed_hour(imei)
                    if data is not None:
                        np_timpestamp = np.array(data.timestamp)
                        np_latitude = np.array(data.latitude)
                        np_longitude = np.array(data.longitude)
                        np_altitude = np.array(data.altitude)
                        np_heading = np.array(data.heading)
                        np_voltage = np.array(data.voltage)
                        np_speed = np.array(data.speed)
                        np_distance = np.array(data.distance_total)
                        np_fuel = np.array(data.fuel)                 
                        np_power_status = np.array(data.power_status)
                        np_operating_status = np.array(data.operating_status)
                        np_device_status = np.array(data.device_status)
                        np_calculation_cycle_status = np.array(data.calculation_cycle_status)
                        np_calculation_hour_status = np.array(data.calculation_hour_status)
                        np_expired_date = np.array(data.expired_date)

                    dt_array = np.column_stack((np_timpestamp, np_latitude, np_longitude, np_altitude, np_heading, np_voltage, np_speed, 
                                                np_distance, np_fuel, np_power_status, np_operating_status, np_device_status, 
                                                np_calculation_cycle_status, np_calculation_hour_status, np_expired_date))
                    

        except Exception as e:
            log_hour.error(f"Error Proses Hour, Error: {e}")