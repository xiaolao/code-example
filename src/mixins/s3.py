import io
import aiofiles
import aiobotocore

from tenacity import retry, stop_after_attempt

from .base import BaseMixIn, BaseContext
from src.models.options import S3ContextOption


class S3Context(BaseContext, attr_name="s3"):

    def __init__(self, option: S3ContextOption):
        self.option = option

    async def __aenter__(self):
        session = aiobotocore.get_session()
        self.client = session.create_client(self.option.service_name,
                                            region_name=self.option.region_name,
                                            config=self.option.config)
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()


class S3MixIn(BaseMixIn, context=S3Context):

    async def get_object(self, bucket, key):
        response = await self.s3.get_object(Bucket=bucket, Key=key)
        async with response['Body'] as stream:
            return io.StringIO((await stream.read()).decode())

    @retry(stop=stop_after_attempt(4), reraise=True)
    async def download_file(self, bucket, key, file_name):
        response = await self.s3.get_object(Bucket=bucket, Key=key)
        async with response['Body'] as stream, aiofiles.open(file_name, "wb") as f:
            await f.write(await stream.read())

    async def list_objects(self, bucket, prefix, start_after=""):
        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(MaxKeys=1000, Bucket=bucket, Prefix=prefix, StartAfter=start_after)
        while True:
            page = await pages.next_page()
            if page is None or not page.get("Contents"):
                break
            for item in page.get("Contents"):
                yield item["Key"]
