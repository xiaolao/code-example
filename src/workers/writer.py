import os
import json
import logging
import asyncio
from traceback import format_exc

from .base import AbcWorker

from src.models.constants import Status
from src.models.options import WriteWorkerOption
from src.models.collections import DownloadLog, TextData
from src.mixins import MongoDBMixIn, MonitorMixIn, LogMixIn, ManagerMixIn


logger = logging.getLogger("sync")


class WriteWorker(AbcWorker, MongoDBMixIn, MonitorMixIn, LogMixIn, ManagerMixIn):
    """Read json file and write text data into mongodb by order"""

    def __init__(self, option: WriteWorkerOption):
        self.option = option

    # async def start(self):
    #     worker_count = await self.get_worker_count(self.option.worker_name)
    #     if worker_count > 1:
    #         raise Exception(f"{self.__class__.__name__} can't run consurrently")

    async def write(self, recode: DownloadLog):
        try:
            json_path = recode.json_path
            message = f"Error: {self.__class__.__name__} 同步 {recode.json_path} 失败"
            async with self.monitor(message):
                with open(json_path, "r") as reader:
                    for line in reader:
                        await self.write_data(TextData(**json.loads(line)))
                await self.find_update_by_id(recode._id, Status.END_WRITE)
                logger.info(f"{self.__class__.__name__}: pk {recode._id}")
        except Exception as exc:
            logger.error(f"{self.__class__.__name__}: pk {recode._id}")
            logger.error(format_exc())
            await self.find_update_by_id(recode._id, Status.END_EXTRACT)
            raise exc

    async def run(self):
        # TODO: 并发情况下会有顺序问题，后面要改成用find对id排序取数据。
        # await self.start()
        while True:
            if not await self.switch_on(self.option.worker_name):
                await asyncio.sleep(self.option.interval)
                continue
            recode = await self.find_update_by_status(Status.END_EXTRACT, Status.START_WRITE)
            if not recode:
                await asyncio.sleep(self.option.interval)
                continue
            await self.write(recode)
