import asyncio
from prisma import Prisma

async def test_connection():
    db = Prisma()
    await db.connect()
    print("Koneksi berhasil!")
    await db.disconnect()

# Panggil fungsi test_connection()
asyncio.run(test_connection())

