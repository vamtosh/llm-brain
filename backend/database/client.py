"""PostgreSQL database client with connection pooling for concurrent users."""

import asyncpg
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/brainstorm_db"
)

# Connection pool settings for 3000 concurrent users
MIN_POOL_SIZE = 10
MAX_POOL_SIZE = 100
MAX_QUERIES = 50000
MAX_INACTIVE_CONNECTION_LIFETIME = 300.0  # 5 minutes


class DatabaseClient:
    """Async PostgreSQL client with connection pooling."""

    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Initialize database connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=MIN_POOL_SIZE,
                max_size=MAX_POOL_SIZE,
                max_queries=MAX_QUERIES,
                max_inactive_connection_lifetime=MAX_INACTIVE_CONNECTION_LIFETIME,
                command_timeout=60
            )
            print(f"✅ Database connection pool created (min={MIN_POOL_SIZE}, max={MAX_POOL_SIZE})")

    async def disconnect(self):
        """Close database connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            print("✅ Database connection pool closed")

    async def execute(self, query: str, *args):
        """Execute a query that doesn't return rows."""
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Fetch multiple rows."""
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Fetch a single row."""
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """Fetch a single value."""
        async with self._pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    @property
    def pool(self) -> asyncpg.Pool:
        """Get the connection pool."""
        if self._pool is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._pool


# Global database instance
db = DatabaseClient()


async def init_db():
    """Initialize database connection."""
    await db.connect()


async def close_db():
    """Close database connection."""
    await db.disconnect()
