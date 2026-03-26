"""
MongoDB Atlas connection layer using Motor (async driver).

Provides:
  - get_database()           → returns the active Motor database instance
  - connect_to_mongo()       → called on app startup via lifespan
  - close_mongo_connection() → called on app shutdown via lifespan
"""

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Module-level handles — set during startup, cleared on shutdown
_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_database() -> AsyncIOMotorDatabase:
    """Return the active Motor database instance.

    Raises:
        RuntimeError: if called before connect_to_mongo() has succeeded.
    """
    if _db is None:
        raise RuntimeError(
            "Database not initialised. Ensure connect_to_mongo() ran at startup."
        )
    return _db


async def connect_to_mongo() -> None:
    """Create the Motor client and verify Atlas connectivity.

    Reads:
        MONGODB_URI   — full Atlas connection string from .env
        DATABASE_NAME — target database name (default: "sevam")

    Prints a success or failure message and logs the result.
    Raises on failure so the app does not start in a broken state.
    """
    global _client, _db

    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DATABASE_NAME", "sevam")

    if not uri:
        raise RuntimeError(
            "MONGODB_URI is not set.\n"
            "Add it to your .env file:\n"
            "  MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/sevam"
        )

    try:
        _client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        _db = _client[db_name]

        # Ping confirms the credentials and network path are valid
        await _client.admin.command("ping")

        print(f"[OK] MongoDB connected  ->  database: '{db_name}'")
        logger.info("MongoDB Atlas connection established (db=%s)", db_name)

    except Exception as exc:
        _client = None
        _db = None
        print(f"[ERROR] MongoDB connection FAILED: {exc}")
        logger.error("MongoDB Atlas connection failed: %s", exc)
        raise


async def close_mongo_connection() -> None:
    """Close the Motor client gracefully on app shutdown."""
    global _client, _db

    if _client is not None:
        _client.close()
        _client = None
        _db = None
        print("[OK] MongoDB connection closed.")
        logger.info("MongoDB Atlas connection closed.")
