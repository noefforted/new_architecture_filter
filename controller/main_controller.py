import asyncio
from asyncio import StreamReader, StreamWriter
import logging
from config.database_connector import database_connector
from scheduler.scheduler import CycleEfficiencyScheduler, HourEfficiencyScheduler
from connectivity.tcp_server import TCPServer, TCPServerCallback
from model.request_controller import IncomingCommand, ResponseStatus, RequestPacket, ResponsePacketRecentReportHour
from connectivity.tcp_server import TCPServer, TCPServerCallback
from service.calculation import EfficiencyService
from util.log import log_begin
from config.database_connector import database_connector


log_begin()
log_app = logging.getLogger("App Controller")
log_tcp = logging.getLogger("TCP Server")

class TCPcallback(TCPServerCallback):
    async def server_handler(self, reader: StreamReader, writer: StreamWriter, db=database_connector.prisma):
        data = await asyncio.wait_for(reader.read(1000), 10)
        if data:
            req = RequestPacket.model_validate_json(data)

            if req.command == IncomingCommand.GET_RECENT_HOUR:

                if not req.payload or "vehicle_id" not in req.payload:
                    log_tcp.info("Received GET_RECENT_HOUR command for all vehicles.")
                    vehicles = await db.vehicle.find_many()
                    vehicle_ids = [val.id for val in vehicles]
                    # log_tcp.info(f"Vehicle IDs: {vehicle_ids}")
                    all_final_data = []
                    for ids in vehicle_ids:
                        final_data = await EfficiencyService.recent_hour_efficiency(ids)
                        all_final_data.extend(final_data)
                    res = ResponsePacketRecentReportHour(command=req.command, status=ResponseStatus.SUCCESS, message="Success", payload=all_final_data)
                    writer.write(res.model_dump_json().encode("utf-8"))
                    log_tcp.info("Response all vehicles sent to client.")
                    await writer.drain()

                else:
                    vehicle_id = req.payload["vehicle_id"]
                    log_tcp.info(f"Received GET_RECENT_HOUR command. Vehicle ID: {vehicle_id}")
                    final_data = await EfficiencyService.recent_hour_efficiency(vehicle_id)
                    res = ResponsePacketRecentReportHour(command=req.command, status=ResponseStatus.SUCCESS, message="Success", payload=final_data)
                    writer.write(res.model_dump_json().encode("utf-8"))
                    log_tcp.info(f"Response for id {vehicle_id} sent to client.")
                    await writer.drain()

            else:
                res = ResponsePacketRecentReportHour(command=req.command, status=ResponseStatus.BAD_REQUEST, message="Bad Request (Command not found)")
                writer.write(res.model_dump_json().encode("utf-8"))
                log_tcp.error("Client sent bad request (Command not found)")
                await writer.drain()

class AppController:
    def __init__(self):
        # Inisialisasi scheduler
        self.cycle_scheduler = CycleEfficiencyScheduler()
        self.hour_scheduler = HourEfficiencyScheduler()

    async def begin(self):
        self.tcp_server = TCPServer(TCPcallback())
        self.sRun = True
        self.sClosed = False
        # Memulai koneksi database dan semua scheduler
        await database_connector.connect()
        log_app.info("Database connected.")

        # Memulai scheduler
        self.cycle_scheduler.start()
        self.hour_scheduler.start()
        log_app.info("All schedulers started.")

    async def close(self):
        self.sRun = False
        while not self.sClosed:
            await asyncio.sleep(1)
        # Menghentikan semua scheduler dan koneksi database
        self.cycle_scheduler.close()
        self.hour_scheduler.close()
        await database_connector.disconnect()
        log_app.info("Database disconnected, all schedulers stopped.")

    async def run(self):
        # Menjaga aplikasi tetap berjalan hingga dihentikan
        try:
            await self.tcp_server.run()
            log_app.info("TCP Server started.")
        except asyncio.CancelledError:
            log_app.info("Application shutdown requested.")
        finally:
            await self.close()
