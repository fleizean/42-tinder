# app/core/migrations.py
import logging
import os
import asyncpg
from app.core.config import settings

logger = logging.getLogger(__name__)

async def run_migrations():
    """Run database migrations"""
    logger.info("Running database migrations...")
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        # Check if migrations table exists
        exists = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'migrations'
        )
        """)
        
        if not exists:
            # Create migrations table
            await conn.execute("""
            CREATE TABLE migrations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
        
        # Get applied migrations
        applied = await conn.fetch("SELECT name FROM migrations")
        applied_names = [row['name'] for row in applied]
        
        # Get all migration files
        migration_dir = os.path.join(os.path.dirname(__file__), '../../migrations')
        migration_files = sorted([f for f in os.listdir(migration_dir) if f.endswith('.sql')])
        
        # Apply migrations in order
        for file_name in migration_files:
            if file_name in applied_names:
                logger.info(f"Migration {file_name} already applied")
                continue
            
            logger.info(f"Applying migration {file_name}...")
            
            # Read migration file
            with open(os.path.join(migration_dir, file_name)) as f:
                sql = f.read()
            
            # Execute migration in a transaction
            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute("INSERT INTO migrations (name) VALUES ($1)", file_name)
            
            logger.info(f"Migration {file_name} applied successfully")
        
        logger.info("Migrations completed successfully")
    
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise
    
    finally:
        await conn.close()