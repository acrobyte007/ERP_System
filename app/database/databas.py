import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
import dotenv
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