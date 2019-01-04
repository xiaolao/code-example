import os
import logging
import asyncio
from traceback import format_exc

from .base import AbcWorker
from src.models.constants import Status
from src.models.collections import DownloadLog
from src.models.options import LoadWorkerOption
from src.mixins import S3MixIn, MonitorMixIn, LogMixIn, ManagerMixIn


logger = logging.getLogger("sync")


class LoadWorker(AbcWorker, LogMixIn, S3MixIn, MonitorMixIn, ManagerMixIn):
    """Download s3 objects by get s3 key from recode using the
    find_and_update_one api.
    """

    def __init__(self, option: LoadWorkerOption):
        self.option = option
        self.bucket = option.path.s3_bucket

    async def download(self, recode: DownloadLog, position: int):
        try:
            key = recode.s3_key
            path = recode.gzip_path
            if os.path.exists(path) and os.stat(path).st_size > 0:
                await self.find_update_by_id(recode._id, Status.END_DOWNLOAD)
                return
            message = f"Error: {self.__class__.__name__} 下载 {key} 失败"
            async with self.monitor(message):
                os.makedirs(path.rsplit("/", 1)[0], exist_ok=True)
                await self.download_file(self.bucket, key, path)
                await self.find_update_by_id(recode._id, Status.END_DOWNLOAD)
                logger.info(f"{self.__class__.__name__}{position}: pk {recode._id}")
        except Exception as exc:
            logger.error(f"{self.__class__.__name__}{position}: pk {recode._id}")
            logger.error(format_exc())
            await self.find_update_by_id(recode._id, Status.CREATED)

    async def task(self, position: int):
        while True:
            if not await self.switch_on(self.option.worker_name):
                await asyncio.sleep(self.option.interval)
                continue
            recode = await self.find_update_by_status(Status.CREATED, Status.START_DOWNLOAD)
            if not recode:
                await asyncio.sleep(self.option.interval)
                continue
            await self.download(recode, position)

    async def run(self):
        tasks = [self.task(position) for position in range(self.option.concurrency)]
        await asyncio.gather(*tasks)
