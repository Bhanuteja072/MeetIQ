from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from typing import Optional

client: Optional[AsyncIOMotorClient] = None
db = None

async def connect_db() -> None:
    global client, db
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.database_name]
        print(f"✅ Connected to MongoDB: {settings.database_name}")
    except Exception as e:
        raise RuntimeError(f"MongoDB connection failed: {e}")
async def close_db() -> None:
    global client
    if client:
        client.close()
        print("🔌 MongoDB connection closed")

def get_db() -> Optional[AsyncIOMotorClient]:
    return db

# # FastAPI dependency
# async def get_database() -> Optional[AsyncIOMotorClient]:
#     return db