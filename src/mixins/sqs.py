import aiobotocore

from .base import BaseContext, BaseMixIn
from src.models.options import SqsContextOption


class SqsContext(BaseContext, attr_name="sqs"):

    def __init__(self, option: SqsContextOption):
        self.option = option

    async def __aenter__(self):
        session = aiobotocore.get_session()
        self.client = session.create_client(self.option.service_name,
                                            region_name=self.option.region_name,
                                            config=self.option.config)
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()


class SqsMixIn(BaseMixIn, context=SqsContext):

    async def receive_message(self, queue_url):
        response = await self.sqs.receive_message(QueueUrl=queue_url)
        return response.get("Messages")

    async def get_queue_url(self, queue_name):
        return (await self.sqs.get_queue_url(QueueName=queue_name)).get("QueueUrl")

    async def delete_sqs_msg(self, queue_url, receipt):
        await self.sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt)
