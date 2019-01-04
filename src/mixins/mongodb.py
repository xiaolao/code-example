import json
import aiomongo

from .base import BaseContext, BaseMixIn
from src.models.collections import TextData
from src.models.options import MongoDBContextOption


class MongoDBContext(BaseContext, attr_name="mongodb"):

    def __init__(self, option: MongoDBContextOption):
        self.option = option

    async def __aenter__(self) -> aiomongo.AioMongoClient:
        self.client = await aiomongo.create_client(uri=self.option.uri)
        self.database = self.client.get_database(self.option.database)
        return self.database

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


class MongoDBMixIn(BaseMixIn, context=MongoDBContext):

    async def write_data(self, text_data: TextData):
        event_name = text_data.event.lower()
        table = self.mongodb.get_collection(text_data.table)
        if event_name == "remove":
            await table.delete_one({"_id": text_data.pk})
        else:
            await table.replace_one({"_id": text_data.pk}, text_data.image, upsert=True)
