import os
import logging
import asyncio
from traceback import format_exc

from .base import AbcWorker
from src.models.constants import Status
from src.models.collections import DownloadLog
from src.models.options import ExtractWorkerOption
from src.mixins import MonitorMixIn, ProcessMixIn, LogMixIn, ManagerMixIn, handler


logger = logging.getLogger("sync")


class ExtractWorker(AbcWorker, LogMixIn, MonitorMixIn, ProcessMixIn, ManagerMixIn):
    """Decompress gzip files which are downloaded from s3 to the specified local path"""

    def __init__(self, option: ExtractWorkerOption):
        self.option = option
        self.loop = option.loop

    async def extract(self, recode: DownloadLog, position: int):
        try:
            gzip_path = recode.gzip_path
            json_path = recode.json_path
            table_name = recode.table_name
            message = f"Error: {self.__class__.__name__} 解压 {gzip_path} 失败"
            async with self.monitor(message):
                os.makedirs(os.path.dirname(json_path), exist_ok=True)
                await self.loop.run_in_executor(self.process_executor, handler, gzip_path, json_path, table_name)
                await self.find_update_by_id(recode._id, Status.END_EXTRACT)
                logger.info(f"{self.__class__.__name__}{position}: pk {recode._id}")
        except Exception as exc:
            logger.error(f"{self.__class__.__name__}{position}: pk {recode._id}")
            logger.error(format_exc())
            await self.find_update_by_id(recode._id, Status.END_DOWNLOAD)

    async def task(self, position: int):
        while True:
            if not await self.switch_on(self.option.worker_name):
                await asyncio.sleep(self.option.interval)
                continue
            recode = await self.find_update_by_status(Status.END_DOWNLOAD, Status.START_EXTRACT)
            if not recode:
                await asyncio.sleep(self.option.interval)
                continue
            await self.extract(recode, position)

    async def run(self):
        tasks = [self.task(position) for position in range(self.option.concurrency)]
        await asyncio.gather(*tasks)
