import os
import typing
import asyncio
import logging

from hashlib import md5
from traceback import format_exc
from datetime import datetime

from .base import AbcWorker
from src.models.constants import Status
from src.models.options import RecodeWorkerOption
from src.models.constants import DynamoDBTables
from src.models.collections import DownloadLog
from src.mixins import ManagerMixIn, S3MixIn, MonitorMixIn, LogMixIn


logger = logging.getLogger("sync")


class RecodeWorker(AbcWorker, ManagerMixIn, LogMixIn, S3MixIn, MonitorMixIn):
    """list s3 objects and save recode log to the download_log collection."""

    def __init__(self, option: RecodeWorkerOption):
        self.option = option
        self.path = option.path
        self.s3_bucket = option.path.s3_bucket
        self.s3_prefix = option.path.s3_prefix

    async def generator(self) -> typing.AsyncGenerator:
        while True:
            if not await self.switch_on(self.option.worker_name):
                await asyncio.sleep(self.option.interval)
                continue
            for table in DynamoDBTables:
                start_after = await self.get_start_after(table.value)
                prefix = os.path.join(self.s3_prefix, table.value)
                async for key in self.list_objects(self.s3_bucket, prefix, start_after):
                    yield table.value, key
            await asyncio.sleep(self.option.interval)

    async def save(self, recode: DownloadLog):
        try:
            message = f"Error: {self.__class__.__name__} 记录 {recode.s3_key} 失败"
            async with self.monitor(message):
                await self.create_log(recode)
                logger.info(f"{self.__class__.__name__}: pk {recode._id}")
        except Exception as exc:
            logger.critical(f"{self.__class__.__name__}: pk {recode.s3_key}")
            logger.critical(format_exc())
            raise exc

    async def run(self):
        async for table_name, key in self.generator():
            hash_id = md5(key.encode()).hexdigest()
            if await self.hash_exists(hash_id):
                continue
            path = key.lstrip(self.path.s3_prefix)
            gzip_path = os.path.join(self.path.gzip_file_dir, path)
            json_path = os.path.join(self.path.json_file_dir, path)
            recode = DownloadLog(
                s3_key=key,
                hash_id=hash_id,
                table_name=table_name,
                gzip_path=gzip_path,
                json_path=json_path,
                status=Status.CREATED,
                created_time=datetime.now(),
                _id=await self.get_next_id(),
            )
            await self.save(recode)

