from concurrent.futures import ProcessPoolExecutor

from .base import BaseContext, BaseMixIn
from src.models.options import ProcessContextOption


class ProcessContext(BaseContext, attr_name="process_executor"):

    def __init__(self, option: ProcessContextOption):
        self.option = option

    def __enter__(self) -> ProcessPoolExecutor:
        self.process_executor = ProcessPoolExecutor(max_workers=self.option.max_workers)
        return self.process_executor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.process_executor.shutdown(wait=True)


class ProcessMixIn(BaseMixIn, context=ProcessContext):
    pass
