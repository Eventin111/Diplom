import sys

from app.infrastructure.cache import tryon_rate_limit as _tryon_rate_limit


sys.modules[__name__] = _tryon_rate_limit
