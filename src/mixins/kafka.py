import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from .base import BaseContext, BaseMixIn
from src.models.options import KafkaConsumerOption, KafkaProducerOption


class KafkaConsumerContext(BaseContext, attr_name="kafka_consumer"):

    def __init__(self, option: KafkaConsumerOption):
        self.option = option
        self.loop = option.loop
        self.topic = option.topic
        self.group_id = option.group_id
        self.brokers = option.brokers

    async def __aenter__(self):
        self.consumer = AIOKafkaConsumer(self.topic, bootstrap_servers=self.brokers,
                                         group_id=self.group_id, loop=self.loop)
        await self.consumer.start()
        return self.consumer

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.consumer.stop()


class KafkaProducerContext(BaseContext, attr_name="kafka_producer"):

    def __init__(self, option: KafkaProducerOption):
        self.option = option
        self.loop = option.loop
        self.brokers = option.brokers

    async def __aenter__(self):
        self.producer = AIOKafkaProducer(loop=self.loop, bootstrap_servers=self.brokers)
        await self.producer.start()
        return self.producer

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.producer.stop()


class KafkaConsumerMixIn(BaseMixIn, context=KafkaConsumerContext):
    pass


class KafkaProducerMixIn(BaseMixIn, context=KafkaProducerContext):

    async def send_and_wait(self, topic: str, message: str):
        await self.kafka_producer.send_and_wait(topic, value=message.encode())
