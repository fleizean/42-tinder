import asyncpg
import psycopg2
from app.core.config import settings


async def get_connection():
    """Get a database connection"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

# Synchronous alternative using psycopg2 if needed
def get_db_connection():
    """Get a synchronous database connection"""
    conn = psycopg2.connect(settings.DATABASE_URL)
    return conn