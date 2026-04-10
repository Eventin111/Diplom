import sys

from app.infrastructure.cache import tryon_cache as _tryon_cache

sys.modules[__name__] = _tryon_cache
