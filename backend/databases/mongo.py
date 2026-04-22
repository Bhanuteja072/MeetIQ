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
        # Ensure unique index on email — prevents race condition duplicates
        await db.users.create_index("email", unique=True)
        # Speed up per-user meeting queries
        await db.meetings.create_index("user_id")
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