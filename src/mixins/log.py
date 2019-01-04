import typing
import pymongo
import aiomongo
from datetime import datetime

from .base import BaseContext, BaseMixIn
from src.models.options import LogContextOption
from src.models.collections import DownloadLog


class LogContext(BaseContext, attr_name="log"):

    def __init__(self, option: LogContextOption):
        self.option = option

    async def __aenter__(self) -> aiomongo.Collection:
        self.client = await aiomongo.create_client(uri=self.option.uri)
        database = self.client.get_database(self.option.database)
        self.table = database.get_collection(self.option.collection)
        return self.table

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


class LogMixIn(BaseMixIn, context=LogContext):

    async def get_start_after(self, table_name) -> str:
        recode = await self.log.find_one({"table_name": table_name}, sort=[("_id", pymongo.DESCENDING)])
        return recode.get("s3_key") if recode else ""

    async def hash_exists(self, hash_id: str) -> bool:
        recode = await self.log.find_one({"hash_id": hash_id})
        return True if recode else False

    async def create_log(self, recode: DownloadLog):
        await self.log.insert_one(vars(recode))

    async def find_update_by_status(self, before: int, after: int) -> DownloadLog:
        result = await self.log.find_one_and_update({"status": before},
                                                  {"$set": {"status": after, "updated_time": datetime.now()}},
                                                  sort=[("_id", pymongo.ASCENDING)], new=True)
        return DownloadLog(**result) if result else None

    async def find_update_by_id(self, pk: int, status: int) -> DownloadLog:
        result = await self.log.find_one_and_update({"_id": pk},
                                                    {"$set": {"status": status, "updated_time": datetime.now()}})
        return DownloadLog(**result) if result else None
