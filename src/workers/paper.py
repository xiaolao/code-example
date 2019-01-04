import os
import time
import json
import typing
import logging
import asyncio

from hashlib import md5
from datetime import datetime
from traceback import format_exc

from .base import AbcWorker
from src.models.constants import Status
from src.utils import decompress, DecimalEncoder
from src.models.options import PaperWorkerOption
from src.models.collections import DownloadLog, TextData
from src.mixins import MonitorMixIn, ManagerMixIn, S3MixIn, LogMixIn, DynamoDBMixIn, ProcessMixIn


logger = logging.getLogger("sync")


class PaperWorker(AbcWorker, MonitorMixIn, ManagerMixIn, S3MixIn, LogMixIn, DynamoDBMixIn, ProcessMixIn):

    def __init__(self, option: PaperWorkerOption):
        self.option = option
        self.path = option.path
        self.loop = option.loop

    async def generator(self) -> typing.AsyncGenerator:
        while True:
            if not await self.switch_on(self.option.worker_name):
                await asyncio.sleep(self.option.interval)
                continue
            start_after = await self.get_start_after(self.option.dynamo_table)
            async for key in self.list_objects(self.path.s3_bucket, self.path.s3_prefix, start_after):
                yield key
            await asyncio.sleep(self.option.interval)

    async def write(self, f, lines):
        for line in lines:
            image = ""
            pk = (line.split("|")[0]).strip()
            event = (line.split("|")[1]).strip("\n")
            key = {self.option.dynamo_index: {"S": pk}}
            if event != "REMOVE":
                image = await self.get_item(self.option.dynamo_table, key)
                if not image:
                    continue
                image.pop("ack", None)
                image.pop("media", None)
                image.pop("xrefs", None)
                image["updated_ts"] = int(time.time())
                image = await self.loop.run_in_executor(self.process_executor, decompress, image)
            text_data = TextData(pk=pk, event=event, image=image, table=self.option.mongodb_table)
            f.write(json.dumps(vars(text_data), cls=DecimalEncoder)+"\n")

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
        async for key in self.generator():
            hash_id = md5(key.encode()).hexdigest()
            if await self.hash_exists(hash_id):
                continue
            path = key.lstrip(self.path.s3_prefix)
            json_path = os.path.join(self.path.json_file_dir, self.option.dynamo_table, path)
            message = f"Error: {self.__class__.__name__} 同步 {key} 失败"
            async with self.monitor(message):
                os.makedirs(json_path.rsplit("/", 1)[0], exist_ok=True)
                lines = await self.get_object(self.path.s3_bucket, key)
                with open(json_path, "w") as f:
                    await asyncio.gather(*[self.write(f, lines) for _ in range(self.option.concurrency)])
                recode = DownloadLog(
                    s3_key=key,
                    hash_id=hash_id,
                    table_name=self.option.dynamo_table,
                    json_path=json_path,
                    created_time=datetime.now(),
                    _id=await self.get_next_id(),
                    status=Status.END_EXTRACT,
                )
                await self.save(recode)
