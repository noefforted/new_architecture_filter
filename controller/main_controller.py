import asyncio
import logging
from config.database_connector import database_connector
from scheduler.scheduler import CycleEfficiencyScheduler, HourEfficiencyScheduler

log = logging.getLogger("Controller")

class AppController:
    def __init__(self):
        # Inisialisasi scheduler
        self.cycle_scheduler = CycleEfficiencyScheduler()
        self.hour_scheduler = HourEfficiencyScheduler()

    async def begin(self):
        # Memulai koneksi database dan semua scheduler
        await database_connector.connect()
        log.info("Database connected.")

        # Memulai scheduler
        self.cycle_scheduler.start()
        self.hour_scheduler.start()
        log.info("All schedulers started.")

    async def close(self):
        # Menghentikan semua scheduler dan koneksi database
        self.cycle_scheduler.close()
        self.hour_scheduler.close()
        await database_connector.disconnect()
        log.info("Database disconnected, all schedulers stopped.")

    async def run(self):
        # Menjaga aplikasi tetap berjalan hingga dihentikan
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            log.info("Application shutdown requested.")
        finally:
            await self.close()
