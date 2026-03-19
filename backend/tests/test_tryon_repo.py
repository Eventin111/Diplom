import asyncio

from app.schemas.tryon import TryOnStatus


class DummyResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows

    def scalars(self):
        class ScalarWrapper:
            def __init__(self, values):
                self._values = values

            def all(self):
                return self._values

        return ScalarWrapper(self._rows)


class DummySession:
    def __init__(self, execute_results):
        self._execute_results = list(execute_results)

    async def execute(self, query):
        return self._execute_results.pop(0)


class FailedSession:
    def __init__(self, session_id, user_id, error_text, updated_at):
        self.id = session_id
        self.user_id = user_id
        self.error_text = error_text
        self.updated_at = updated_at
        self.created_at = updated_at


def test_get_status_counts_fills_missing_statuses():
    from app.repositories.tryon_repo import TryOnRepository

    repo = TryOnRepository()
    db = DummySession([DummyResult([(TryOnStatus.QUEUED, 2), (TryOnStatus.COMPLETED, 5)])])

    counts = asyncio.run(repo.get_status_counts(db))

    assert counts == {
        "queued": 2,
        "processing": 0,
        "completed": 5,
        "failed": 0,
    }


def test_get_recent_failures_serializes_failure_payload():
    from datetime import datetime
    from app.repositories.tryon_repo import TryOnRepository

    repo = TryOnRepository()
    db = DummySession(
        [
            DummyResult(
                [
                    FailedSession(7, 9, "boom", datetime(2026, 3, 19, 12, 0, 0)),
                ]
            )
        ]
    )

    failures = asyncio.run(repo.get_recent_failures(db, limit=5))

    assert failures == [
        {
            "session_id": 7,
            "user_id": 9,
            "error_text": "boom",
            "updated_at": "2026-03-19T12:00:00",
        }
    ]
