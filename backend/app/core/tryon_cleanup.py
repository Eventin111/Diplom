import sys

from app.infrastructure.maintenance import tryon_cleanup as _tryon_cleanup

sys.modules[__name__] = _tryon_cleanup
