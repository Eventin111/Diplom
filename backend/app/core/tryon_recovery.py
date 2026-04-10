import sys

from app.infrastructure.maintenance import tryon_recovery as _tryon_recovery

sys.modules[__name__] = _tryon_recovery
