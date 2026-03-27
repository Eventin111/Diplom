import sys

from app.infrastructure.queue import tryon_queue as _tryon_queue


sys.modules[__name__] = _tryon_queue
