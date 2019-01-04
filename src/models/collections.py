import typing

from datetime import datetime
from dataclasses import dataclass


@dataclass
class DownloadLog:
    # 根据顺序的自增id
    _id: int = 0
    # 该文件的同步状态
    status: int = 0
    # 触发该文件的dynamodb table name
    table_name: str = ""
    # 根据s3_key生成的hash值，用做unique索引
    hash_id: str = ""
    # 文件在s3上的路劲
    s3_key: str = ""
    # 原始gzip文件在本地的路径
    gzip_path: str = ""
    # 解压后的文件在本地的路径
    json_path: str = ""
    # 记录的创建时间
    created_time: datetime = datetime.now()
    # 记录的更新时间
    updated_time: datetime = datetime.now()


@dataclass
class DownloadManager:
    # 用worker的类名做id
    _id: str
    # 同步开关
    switch: bool = True
    # 当前运行的worker数量
    count: int = 0


@dataclass
class TextData:
    pk: str = ""
    table: str = ""
    image: dict = None
    event: str = ""
    sequence: str = ""
