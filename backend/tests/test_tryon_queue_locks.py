import asyncio
import importlib
import sys


class FakeRedis:
    def __init__(self, scan_batches):
        self.scan_batches = list(scan_batches)

    async def scan(self, cursor=0, match=None, count=100):
        return self.scan_batches.pop(0)


def reload_tryon_queue_module():
    sys.modules.pop("app.core.tryon_queue", None)
    return importlib.import_module("app.core.tryon_queue")


def test_get_tryon_processing_lock_count_sums_scan_batches(monkeypatch):
    module = reload_tryon_queue_module()
    fake_redis = FakeRedis(
        scan_batches=[
            (1, ["tryon:processing:1", "tryon:processing:2"]),
            (0, ["tryon:processing:3"]),
        ]
    )
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)

    count = asyncio.run(module.get_tryon_processing_lock_count())

    assert count == 3
