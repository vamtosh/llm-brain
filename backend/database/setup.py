"""Database setup and migration script."""

import asyncio
import asyncpg
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/brainstorm_db"
)


async def setup_database():
    """Create database if it doesn't exist and run schema."""
    # Parse connection details
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL)

    db_name = parsed.path[1:]  # Remove leading /
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port or 5432

    # Connect to postgres database to create our database
    conn = await asyncpg.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database='postgres'
    )

    try:
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            db_name
        )

        if not exists:
            # Create database
            await conn.execute(f'CREATE DATABASE {db_name}')
            print(f"✅ Database '{db_name}' created")
        else:
            print(f"✅ Database '{db_name}' already exists")

    finally:
        await conn.close()

    # Now connect to our database and run schema
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Read schema file
        schema_path = Path(__file__).parent / "schema.sql"
        schema_sql = schema_path.read_text()

        # Execute schema
        await conn.execute(schema_sql)
        print("✅ Database schema created/updated")

    finally:
        await conn.close()


if __name__ == "__main__":
    print("🚀 Setting up database...")
    asyncio.run(setup_database())
    print("✅ Database setup complete!")
