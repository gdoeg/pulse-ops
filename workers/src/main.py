"""Worker process entrypoint for PulseOps background workloads."""

import asyncio
import signal

from src.config import get_settings
from src.database import WorkerDatabase
from src.logging import configure_logging, get_logger
from src.monitor import MonitorWorker
from src.queue import TaskQueue


def healthcheck() -> dict[str, str]:
    """Placeholder healthcheck used by worker supervisors."""
    return {"status": "ok"}


async def _main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level, settings.environment)
    logger = get_logger(__name__)

    database = WorkerDatabase(settings)
    queue = TaskQueue(settings)

    await database.initialize()
    await queue.initialize()

    worker = MonitorWorker(settings, database, queue)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, worker.request_shutdown)

    logger.info("pulseops worker process started")
    try:
        await worker.run()
    finally:
        await queue.close()
        await database.close()
        logger.info("pulseops worker process stopped")


if __name__ == "__main__":
    asyncio.run(_main())
