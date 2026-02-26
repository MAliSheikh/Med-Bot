import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

uri = "mongodb+srv://malisheikh:KQshXA4XAHCgGmdS@cluster0.9hiztwt.mongodb.net/?appName=Cluster0"
client = AsyncIOMotorClient(uri)
db = client.test  # test database

async def test_connection():
    try:
        await client.admin.command("ping")
        print("Pinged your deployment. Successfully connected to MongoDB!")
    except Exception as e:
        print(e)

asyncio.run(test_connection())