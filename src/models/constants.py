from enum import IntEnum, Enum, unique


@unique
class Status(IntEnum):
    # recoder worker
    CREATED = 0
    # download worker
    START_DOWNLOAD = -1
    END_DOWNLOAD = 1
    # extract worker
    START_EXTRACT = -2
    END_EXTRACT = 2
    # write worker
    START_WRITE = -9
    END_WRITE = 9


@unique
class DynamoDBTables(Enum):
    ENTITY = "360_entity"
    REPOSITORY = "360_repository"
