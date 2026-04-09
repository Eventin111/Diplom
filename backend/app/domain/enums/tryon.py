from enum import Enum


class TryOnStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class TryOnEventType(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    RETRY = "retry"
    RECOVERED = "recovered"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    DEAD_LETTERED = "dead_lettered"
