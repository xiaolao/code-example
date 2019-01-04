import aiobotocore

from src.utils import deserialize
from .base import BaseContext, BaseMixIn
from src.models.options import DynamoDBContextOption


class DynamoDBContext(BaseContext, attr_name="dynamodb"):

    def __init__(self, option: DynamoDBContextOption):
        self.option = option

    async def __aenter__(self):
        session = aiobotocore.get_session()
        self.client = session.create_client(self.option.service_name,
                                            region_name=self.option.region_name,
                                            config=self.option.config)
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()


class DynamoDBMixIn(BaseMixIn, context=DynamoDBContext):

    async def get_item(self, table_name: str, key: dict):
        item = await self.dynamodb.get_item(TableName=table_name, Key=key)
        return deserialize(item.get('Item', {}))
