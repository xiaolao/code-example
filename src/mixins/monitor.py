import logging
from traceback import format_exc
from aiohttp.client import ClientSession

from .base import BaseContext, BaseMixIn
from src.utils import partial_class
from src.models.options import MonitorContextOption


logger = logging.getLogger("sync")


class Monitor:

    def __init__(self, session: ClientSession, url: str, robot_api: str, message: str, suppress: bool =False):
        self.url = url
        self.suppress = suppress
        self.message = message
        self.session = session
        self.robot_api = robot_api

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            message = "\n".join([self.message, format_exc()])
            await self.session.post(self.url, data={"data": message, "url": self.robot_api})
        return self.suppress


class MonitorContext(BaseContext, attr_name="monitor"):

    def __init__(self, option: MonitorContextOption):
        self.option = option
        self.url = option.url
        self.robot_api = option.robot_api

    async def __aenter__(self):
        self.session = ClientSession()
        return partial_class(Monitor, self.session, self.url, self.robot_api)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            message = "\n".join(["下载程序异常退出", format_exc()])
            await self.session.post(self.url, data={"data": message, "url": self.robot_api})
        await self.session.close()


class MonitorMixIn(BaseMixIn, context=MonitorContext):
    pass
