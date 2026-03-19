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

    async def lindex(self, queue_name, index):
        values = [payload for queued_name, payload in self.items if queued_name == queue_name]
        if index < 0 or index >= len(values):
            return None
        return values[index]

    async def lset(self, queue_name, index, value):
        seen = -1
        for item_index, (queued_name, payload) in enumerate(self.items):
            if queued_name != queue_name:
                continue
            seen += 1
            if seen == index:
                self.items[item_index] = (queued_name, value)
                return True
        raise IndexError

    async def lrem(self, queue_name, count, value):
        removed = 0
        updated = []
        for queued_name, payload in self.items:
            if queued_name == queue_name and payload == value and removed < count:
                removed += 1
                continue
            updated.append((queued_name, payload))
        self.items = updated
        return removed


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
            "index": 0,
        }
    ]


def test_requeue_dead_letter_moves_task_back_to_main_queue(monkeypatch):
    module = reload_tryon_queue_module()
    fake_redis = FakeRedis()
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)

    async def scenario():
        await module.enqueue_tryon_dead_letter({"session_id": 7, "attempt": 2}, "boom")
        return await module.requeue_tryon_dead_letter(0)

    payload = asyncio.run(scenario())

    assert payload == {
        "requeued_task": {"session_id": 7, "attempt": 0},
        "previous_error_text": "boom",
        "requeued_from_index": 0,
    }
    assert fake_redis.items == [
        (module.settings.TRYON_QUEUE_NAME, '{"session_id":7,"attempt":0}')
    ]
