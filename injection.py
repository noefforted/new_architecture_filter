import httpx
import asyncio
import json
from datetime import datetime, timezone
from config.database_connector import database_connector
import logging
from dotenv import load_dotenv
from util.log import log_begin

load_dotenv(override=True)

log_begin()
log = logging.getLogger("Inject")

async def insert_log(imei, timestamp, latitude, longitude, heading, voltage, speed, distance, fuel_level, fuel_consumption, power_status, operate_status, device_status):
    """
    Fungsi untuk memasukkan data ke tabel data_teltonika_buffer dan vehicle.
    """
    # Cek apakah vehicle_id ada berdasarkan IMEI
    vehicle = await database_connector.prisma.vehicle.find_first(
        where={"imei": imei}
    )

    # Jika vehicle belum ada, buat data baru
    if not vehicle:
        vehicle = await database_connector.prisma.vehicle.create(
            data={"imei": imei, "speed_threshold": speed, "fuel_calibration_coefficients": []}
        )

    # Pastikan vehicle memiliki ID
    vehicle_id = vehicle.id if vehicle else None
    if vehicle_id is None:
        raise ValueError("Vehicle ID is required but not found or created")

    # Konversi timestamp ke format DateTime yang kompatibel dengan Prisma
    timestamp_dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)

    # Masukkan data ke tabel data_teltonika_buffer
    await database_connector.prisma.data_teltonika_buffer.create(
        data={
            "timestamp": timestamp_dt,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": 0,
            "angle": heading,
            "speed": speed,
            "battery_voltage": voltage,
            "total_odometer": distance,
            "fuel_level": fuel_level,
            "fuel_used_gps": fuel_consumption,
            "fuel_rate_gps": 0,
            "power_input": 0,
            "operate_status": operate_status,
            "digital_input_2": device_status,
            "gsm_signal": 0,
            "ignition_on_counter": 0,
            "data_payload": json.dumps({}),  # Pastikan `data_payload` adalah JSON
            "vehicle_id": vehicle_id,  # Menggunakan vehicle_id yang valid
            "calculation_cycle_status": False,
            "calculation_hour_status": False
        }
    )

async def main():
    log.info("Connecting to database")
    await database_connector.connect()

    async with httpx.AsyncClient() as client:
        response = await client.get("http://34.101.83.107:50001/api/datalog?limit=75000")
        data = json.loads(response.text)[::-1]  # Membalikkan urutan data jika diperlukan

        for entry in data:
            imei = entry["imei"]
            # Mengonversi timestamp ke UTC datetime
            timestamp = datetime.strptime(entry["timestamp"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            latitude = entry.get("latitude", 0.0)
            longitude = entry.get("longitude", 0.0)
            heading = entry.get("heading", 0)
            voltage = entry.get("voltage", 0)
            speed = entry.get("speed", 0)
            distance = entry.get("distance_total", 0)
            fuel_level = entry.get("fuel", 0)
            fuel_consumption = entry.get("fuel_consumption", 0)
            power_status = entry.get("power_status", False)
            operate_status = entry.get("operate_status", False)
            device_status = entry.get("device_status", False)

            # Log setiap entry untuk verifikasi
            log.info(f"Processing IMEI: {imei}, Timestamp: {timestamp}")

            # Masukkan data ke database
            await insert_log(
                imei, timestamp.timestamp(), latitude, longitude, heading, voltage, speed, 
                distance, fuel_level, fuel_consumption, power_status, operate_status, device_status
            )

    await database_connector.disconnect()
    log.info("Disconnected from database")

# Menjalankan fungsi utama
asyncio.run(main())
