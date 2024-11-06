import asyncio
import logging
import traceback
from dotenv import load_dotenv
from util.log import log_begin
from controller.main_controller import AppController

# Memuat variabel lingkungan
load_dotenv(override=True)

# Inisialisasi logging
log_begin()
log = logging.getLogger("main")

async def main():
    controller = AppController()
    await controller.begin()
    await controller.run()

# Menjalankan fungsi utama jika file ini dijalankan langsung
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (Exception, KeyboardInterrupt):
        log.info("Application shutdown:")
        log.info(traceback.format_exc())
