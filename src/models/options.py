import asyncio

from dataclasses import dataclass
from botocore.config import Config


@dataclass
class FilePathOption:
    s3_bucket: str = ""
    s3_prefix: str = ""
    gzip_file_dir: str = ""
    json_file_dir: str = ""
    host_address: str = ""


@dataclass
class MongoDBContextOption:
    uri: str = ""
    database: str = ""


@dataclass
class AwsOption:
    region_name: str = ""


@dataclass
class S3ContextOption(AwsOption):
    service_name: str = "s3"
    config: Config = None


@dataclass
class DynamoDBContextOption(AwsOption):
    service_name: str = "dynamodb"
    config: Config = None


class SqsContextOption(AwsOption):
    service_name: str = "sqs"
    config: Config = None


@dataclass
class MonitorContextOption:
    url: str = ""
    robot_api: int = ""


@dataclass
class ManagerContextOption(MongoDBContextOption):
    database: str = ""
    # manager download manager
    collection: str = ""
    # worker class name
    worker_name: str = ""


@dataclass
class LogContextOption(MongoDBContextOption):
    database: str = ""
    collection: str = ""


@dataclass
class KafkaContextOption:
    brokers: str = ""


@dataclass
class KafkaConsumerOption(KafkaContextOption):
    topic: str = ""
    group_id: str = ""


@dataclass
class KafkaProducerOption(KafkaContextOption):
    pass


@dataclass
class ProcessContextOption:
    max_workers: int = 4


@dataclass
class MonitorOption:
    url: str = ""
    robot_api: str = ""


@dataclass
class WorkerOption:
    worker_name: str = ""
    interval: int = 60 * 10
    contexts: dict = None
    concurrency: int = 0


@dataclass
class RecodeWorkerOption(WorkerOption):
    path: FilePathOption = None


@dataclass
class LoadWorkerOption(WorkerOption):
    path: FilePathOption = None


@dataclass
class ExtractWorkerOption(WorkerOption):
    loop: asyncio.AbstractEventLoop = None


@dataclass
class WriteWorkerOption(WorkerOption):
    pass


@dataclass
class RepairWorkerOption(WorkerOption):
    pass


@dataclass
class PaperWorkerOption(WorkerOption):
    dynamo_table: str = ""
    dynamo_index: str = ""
    mongodb_table: str = ""
    path: FilePathOption = None
    loop: asyncio.AbstractEventLoop = None
