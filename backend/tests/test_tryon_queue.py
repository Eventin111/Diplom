import asyncio
import importlib
import sys


class FakeRedis:
    def __init__(self):
        self.items = []
        self.storage = {}

    async def lpush(self, queue_name, payload):
        self.items.insert(0, (queue_name, payload))

    async def brpop(self, queue_name, timeout=0):
        if not self.items:
            return None
        queued_name, payload = self.items.pop()
        assert queued_name == queue_name
        return queue_name, payload

    async def set(self, key, value, ex=None, nx=False):
        if nx and key in self.storage:
            return False
        self.storage[key] = value
        return True

    async def delete(self, key):
        self.storage.pop(key, None)

    async def get(self, key):
        return self.storage.get(key)

    async def exists(self, key):
        return key in self.storage


def reload_tryon_queue_module():
    sys.modules.pop("app.core.tryon_queue", None)
    return importlib.import_module("app.core.tryon_queue")


def test_build_tryon_task_payload_contains_expected_fields():
    module = reload_tryon_queue_module()

    payload = module.build_tryon_task_payload(
        session_id=1,
        user_id=2,
        avatar_media_id=3,
        cloth_media_id=4,
        model_type="hd",
        category=0,
        scale=2.0,
        num_steps=10,
        num_samples=1,
        seed=42,
        attempt=1,
    )

    assert payload["session_id"] == 1
    assert payload["user_id"] == 2
    assert payload["avatar_media_id"] == 3
    assert payload["cloth_media_id"] == 4
    assert payload["model_type"] == "hd"
    assert payload["attempt"] == 1


def test_enqueue_and_dequeue_tryon_task_roundtrip(monkeypatch):
    module = reload_tryon_queue_module()
    fake_redis = FakeRedis()
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)

    payload = module.build_tryon_task_payload(
        session_id=11,
        user_id=22,
        avatar_media_id=33,
        cloth_media_id=44,
        model_type="dc",
        category=2,
        scale=1.5,
        num_steps=4,
        num_samples=2,
        seed=7,
    )

    async def scenario():
        await module.enqueue_tryon_task(payload)
        return await module.dequeue_tryon_task(timeout_seconds=1)

    restored = asyncio.run(scenario())

    assert restored == payload


def test_processing_lock_acquire_and_release(monkeypatch):
    module = reload_tryon_queue_module()
    fake_redis = FakeRedis()
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)

    async def scenario():
        first = await module.acquire_tryon_processing_lock(99)
        second = await module.acquire_tryon_processing_lock(99)
        await module.release_tryon_processing_lock(99)
        third = await module.acquire_tryon_processing_lock(99)
        return first, second, third

    assert asyncio.run(scenario()) == (True, False, True)


def test_enqueue_task_stores_snapshot_and_can_read_it(monkeypatch):
    module = reload_tryon_queue_module()
    fake_redis = FakeRedis()
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)

    payload = module.build_tryon_task_payload(
        session_id=11,
        user_id=22,
        avatar_media_id=33,
        cloth_media_id=44,
        model_type="dc",
        category=2,
        scale=1.5,
        num_steps=4,
        num_samples=2,
        seed=7,
    )

    async def scenario():
        await module.enqueue_tryon_task(payload)
        return await module.get_tryon_task_snapshot(11)

    restored = asyncio.run(scenario())

    assert restored == payload


def test_cancellation_and_runtime_pid_helpers_roundtrip(monkeypatch):
    module = reload_tryon_queue_module()
    fake_redis = FakeRedis()
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)

    async def scenario():
        await module.request_tryon_cancellation(51)
        canceled_before_clear = await module.is_tryon_cancellation_requested(51)
        await module.set_tryon_runtime_pid(51, 4321)
        runtime_pid = await module.get_tryon_runtime_pid(51)
        await module.clear_tryon_runtime_pid(51)
        runtime_pid_after_clear = await module.get_tryon_runtime_pid(51)
        await module.clear_tryon_cancellation(51)
        canceled_after_clear = await module.is_tryon_cancellation_requested(51)
        return (
            canceled_before_clear,
            runtime_pid,
            runtime_pid_after_clear,
            canceled_after_clear,
        )

    assert asyncio.run(scenario()) == (True, 4321, None, False)
