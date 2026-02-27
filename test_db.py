import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client.test  # test database

async def test_connection():
    try:
        await client.admin.command("ping")
        print("Pinged your deployment. Successfully connected to MongoDB!")
    except Exception as e:
        print(e)

asyncio.run(test_connection())