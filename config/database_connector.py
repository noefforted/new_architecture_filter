from prisma import Prisma

class DatabaseConnector:
    def __init__(self) -> None:
        self.prisma = Prisma()

    async def connect(self):
        await self.prisma.connect()
    
    async def disconnect(self):
        await self.prisma.disconnect()

database_connector = DatabaseConnector()