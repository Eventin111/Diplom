import asyncio
import importlib
import sys

import pytest
from botocore.exceptions import ClientError


def load_s3_module():
    sys.modules.pop("app.core.s3", None)
    return importlib.import_module("app.core.s3")


class FakeClient:
    def __init__(self, head_bucket_error=None, put_object_error=None):
        self.head_bucket_error = head_bucket_error
        self.put_object_error = put_object_error
        self.calls = []

    def head_bucket(self, **kwargs):
        self.calls.append(("head_bucket", kwargs))
        if self.head_bucket_error:
            raise self.head_bucket_error

    def create_bucket(self, **kwargs):
        self.calls.append(("create_bucket", kwargs))

    def put_object(self, **kwargs):
        self.calls.append(("put_object", kwargs))
        if self.put_object_error:
            raise self.put_object_error


def client_error():
    return ClientError({"Error": {"Code": "404", "Message": "missing"}}, "HeadBucket")


def test_client_lazy_initializes_once(monkeypatch):
    module = load_s3_module()
    fake = FakeClient()
    monkeypatch.setattr(module.boto3, "client", lambda *args, **kwargs: fake)

    client = module.S3Client()

    assert client.client is fake
    assert client.client is fake
    assert ("head_bucket", {"Bucket": client.bucket_name}) in fake.calls


def test_initialize_client_creates_bucket_when_missing(monkeypatch):
    module = load_s3_module()
    fake = FakeClient(head_bucket_error=client_error())
    monkeypatch.setattr(module.boto3, "client", lambda *args, **kwargs: fake)

    client = module.S3Client()
    _ = client.client

    assert any(name == "create_bucket" for name, _ in fake.calls)


def test_upload_file_returns_public_url(monkeypatch):
    module = load_s3_module()
    fake = FakeClient()
    monkeypatch.setattr(module.boto3, "client", lambda *args, **kwargs: fake)
    monkeypatch.setattr(module.settings, "S3_PUBLIC_URL", "https://cdn.example.com")

    client = module.S3Client()
    result = asyncio.run(client.upload_file(b"data", "images/a.png", "image/png"))

    assert result == f"https://cdn.example.com/{client.bucket_name}/images/a.png"
    assert any(name == "put_object" for name, _ in fake.calls)


def test_upload_file_raises_when_client_unavailable(monkeypatch):
    module = load_s3_module()

    client = module.S3Client()
    client._initialized = True
    client._client = None

    with pytest.raises(Exception):
        asyncio.run(client.upload_file(b"data", "images/a.png"))


def test_upload_file_wraps_storage_errors(monkeypatch):
    module = load_s3_module()
    fake = FakeClient(put_object_error=RuntimeError("fail"))
    monkeypatch.setattr(module.boto3, "client", lambda *args, **kwargs: fake)

    client = module.S3Client()

    with pytest.raises(Exception, match="S3"):
        asyncio.run(client.upload_file(b"data", "images/a.png"))
