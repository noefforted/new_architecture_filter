import asyncio
from asyncio import StreamReader, StreamWriter
import logging
from abc import ABC, abstractmethod
import os

log = logging.getLogger("TCP Server")

class TCPServerCallback(ABC):
    @abstractmethod
    async def server_handler(self, reader:StreamReader, writer:StreamWriter):
        pass

class TCPServer:
    def __init__(self, tcp_server_callback:TCPServerCallback)->None:
        self.tcp_server = None
        self.tcp_server_callback = tcp_server_callback

    async def __server_callback(self, reader:StreamReader, writer:StreamWriter):
        try:
            await asyncio.wait_for(self.tcp_server_callback.server_handler(reader, writer), timeout=600)
        except asyncio.TimeoutError as timerr:
            log.error(f"TCP Timeout Error: {timerr}")
        except Exception as err:
            log.error(f"TCP Error: {err}")
        writer.close()
        writer.wait_closed()

    def close(self):
        if self.server is not None:
            self.server.close()

    async def run(self):
        host = os.getenv("TCP_SERVER_HOST")
        port = int(os.getenv("TCP_SERVER_PORT"))
        self.server = await asyncio.start_server(self.__server_callback, host, port)
        async with self.server:
            await self.server.serve_forever()
            log.info(f"TCP Server started at {host}:{port}")