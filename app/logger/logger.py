import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import traceback

_executor = ThreadPoolExecutor(max_workers=2)


def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


async def log_info(logger: logging.Logger, message: str):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(_executor, logger.info, message)


async def log_error(logger: logging.Logger, message: str):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(_executor, logger.error, message)


async def log_exception(logger: logging.Logger, error: Exception):
    loop = asyncio.get_running_loop()
    tb = traceback.format_exc()
    await loop.run_in_executor(_executor, logger.error, f"{error}\n{tb}")