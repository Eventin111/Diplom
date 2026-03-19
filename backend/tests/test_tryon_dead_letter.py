import asyncio
import importlib
import sys


class FakeRedis:
    def __init__(self):
        self.items = []

    async def lpush(self, queue_name, payload):
        self.items.insert(0, (queue_name, payload))

    async def lrange(self, queue_name, start, stop):
        return [payload for queued_name, payload in self.items if queued_name == queue_name]


def reload_tryon_queue_module():
    sys.modules.pop("app.core.tryon_queue", None)
    return importlib.import_module("app.core.tryon_queue")


def test_dead_letter_roundtrip(monkeypatch):
    module = reload_tryon_queue_module()
    fake_redis = FakeRedis()
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)

    async def scenario():
        await module.enqueue_tryon_dead_letter({"session_id": 7, "attempt": 2}, "boom")
        return await module.get_tryon_dead_letters(limit=10)

    dead_letters = asyncio.run(scenario())

    assert dead_letters == [
        {
            "task": {"session_id": 7, "attempt": 2},
            "error_text": "boom",
        }
    ]
