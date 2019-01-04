import aiomongo

from .base import BaseContext, BaseMixIn
from src.models.collections import DownloadManager
from src.models.options import ManagerContextOption


class ManagerContext(BaseContext, attr_name="manager"):

    def __init__(self, option: ManagerContextOption):
        self.option = option
        self.worker_name = option.worker_name

    async def create_worker_manager(self):
        worker_manager = DownloadManager(_id=self.worker_name)
        await self.table.insert_one(worker_manager.__dict__)

    async def increase_worker_count(self):
        if not await self.table.find_one({"_id": self.worker_name}):
            await self.create_worker_manager()
        await self.table.find_one_and_update({"_id": self.worker_name}, {"$inc": {"count": 1}})

    async def decrease_worker_count(self):
        await self.table.find_one_and_update({"_id": self.worker_name}, {"$inc": {"count": -1}})

    async def __aenter__(self) -> aiomongo.Collection:
        self.client = await aiomongo.create_client(uri=self.option.uri)
        database = self.client.get_database(self.option.database)
        self.table = database.get_collection(self.option.collection)
        if self.worker_name:
            await self.increase_worker_count()
        return self.table

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.worker_name:
            await self.decrease_worker_count()
        self.client.close()


class ManagerMixIn(BaseMixIn, context=ManagerContext):

    async def switch_on(self, worker_name: str) -> bool:
        recode = await self.manager.find_one({"_id": worker_name})
        return recode.get("switch") if recode else True

    async def get_worker_count(self, worker_name: str) -> int:
        recode = await self.manager.find_one({"_id": worker_name})
        return recode.get("count")

    async def get_next_id(self) -> int:
        result = await self.manager.find_one_and_update({"_id": "sync_log"}, {"$inc": {"count": 1}}, new=True)
        return result.get("count")
