import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
import dotenv
from app.database.models import Base
from app.logger.logger import get_logger, log_info, log_error, log_exception
dotenv.load_dotenv()
logger = get_logger(__name__)
DATABASE_URL = os.getenv("DB_URL")



engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            await log_info(logger, "Session started")
            yield session
        except Exception as e:
            await log_exception(logger, e)
            raise
        finally:
            await log_info(logger, "Session closed")



async def create_tables():
    """Create all tables defined in the models"""
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,  # Set to True to see SQL output
    )
    
    try:
        await log_info(logger, "Creating database tables...")
        
        # This creates all tables defined in Base.metadata
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
        await log_info(logger, "Tables created successfully!")
        
        # Optional: Verify tables were created
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            await log_info(logger, f"Created tables: {[t[0] for t in tables]}")
            
    except Exception as e:
        await log_error(logger, f"Error creating tables: {str(e)}")
        raise
    finally:
        await engine.dispose()
        await log_info(logger, "Engine disposed")


if __name__ == "__main__":


    async def test_connection():
        session: AsyncSession = AsyncSessionLocal()
        try:
            await log_info(logger, "Attempting DB connection...")

            result = await session.execute(text("SELECT NOW();"))
            current_time = result.scalar()

            await log_info(logger, "Connected to DB!")
            await log_info(logger, f"Current time: {current_time}")

        except Exception as e:
            await log_exception(logger, e)

        finally:
            await session.close()
            await log_info(logger, "Session closed")

        await engine.dispose()
        await log_info(logger, "Engine disposed")
    
    asyncio.run(test_connection())
    asyncio.run(create_tables())