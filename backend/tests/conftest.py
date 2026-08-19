import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")

import mongomock
import pytest
from fastapi.testclient import TestClient

import app.core.mongo as mongo_module
from app.core.config import get_settings


@pytest.fixture(autouse=True)
def _fresh_mongomock(monkeypatch):
    """Every test gets a brand-new in-memory Mongo instance so tests never
    leak state into each other, and no real network/DB connection is made."""
    client = mongomock.MongoClient()
    monkeypatch.setattr(mongo_module, "get_client", lambda: client)
    get_settings.cache_clear()
    mongo_module.ensure_indexes()
    yield client


@pytest.fixture
def app_instance(monkeypatch, tmp_path):
    # Route MinIO calls to no-ops in unit tests that don't explicitly exercise storage.
    import app.core.storage as storage_module

    monkeypatch.setattr(storage_module, "ensure_buckets", lambda: None)

    from app.main import app as fastapi_app

    return fastapi_app


@pytest.fixture
def client(app_instance):
    return TestClient(app_instance)


def register_org(client, name="Test Org", sector="finance", email="admin@testorg.com", password="TestPass123!"):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test Admin",
            "email": email,
            "password": password,
            "organisation": {"name": name, "sector": sector, "size": "100-500", "location": "Test City"},
            "language": "en",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
