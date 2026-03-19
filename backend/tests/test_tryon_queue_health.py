import asyncio
import importlib
import sys


class FakeRedis:
    def __init__(self, queue_length=0, ping_ok=True):
        self.queue_length = queue_length
        self.ping_ok = ping_ok

    async def ping(self):
        return self.ping_ok

    async def llen(self, queue_name):
        return self.queue_length


def reload_tryon_queue_module():
    sys.modules.pop("app.core.tryon_queue", None)
    return importlib.import_module("app.core.tryon_queue")


def test_get_tryon_queue_health_reports_ping_and_length(monkeypatch):
    module = reload_tryon_queue_module()
    fake_redis = FakeRedis(queue_length=3, ping_ok=True)
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)

    payload = asyncio.run(module.get_tryon_queue_health())

    assert payload["redis_ok"] is True
    assert payload["queue_length"] == 3
    assert payload["queue_name"] == module.settings.TRYON_QUEUE_NAME
