from enum import Enum


class StatusEnum(int, Enum):
    ACTIVE = 1
    DELETED = 2
    NOT_ACTIVE = 3
