"""Thin CRUD wrappers around PyMongo collections. Repositories never contain
business logic — that lives in app/services. Routes never touch pymongo
directly; they go through a service, which goes through a repository.
"""
from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection

from app.core.mongo import get_db


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def oid(value: Any) -> ObjectId:
    if isinstance(value, ObjectId):
        return value
    try:
        return ObjectId(str(value))
    except InvalidId as exc:
        raise ValueError(f"Invalid id: {value!r}") from exc


def to_str_id(doc: Optional[dict]) -> Optional[dict]:
    if doc is None:
        return None
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    for key, value in list(doc.items()):
        if isinstance(value, ObjectId):
            doc[key] = str(value)
    return doc


class Repository:
    """Generic repository over a single collection."""

    collection_name: str

    def __init__(self, collection_name: Optional[str] = None):
        if collection_name:
            self.collection_name = collection_name

    @property
    def collection(self) -> Collection:
        return get_db()[self.collection_name]

    def insert(self, doc: dict) -> str:
        doc = dict(doc)
        doc.setdefault("created_at", now_utc())
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)

    def get_by_id(self, doc_id: str) -> Optional[dict]:
        return to_str_id(self.collection.find_one({"_id": oid(doc_id)}))

    def find_one(self, query: dict) -> Optional[dict]:
        return to_str_id(self.collection.find_one(query))

    def find(self, query: Optional[dict] = None, sort: Optional[list] = None, limit: int = 0) -> list[dict]:
        cursor = self.collection.find(query or {})
        if sort:
            cursor = cursor.sort(sort)
        if limit:
            cursor = cursor.limit(limit)
        return [to_str_id(d) for d in cursor]

    def update_by_id(self, doc_id: str, update: dict) -> None:
        update = dict(update)
        update["updated_at"] = now_utc()
        self.collection.update_one({"_id": oid(doc_id)}, {"$set": update})

    def delete_by_id(self, doc_id: str) -> None:
        self.collection.delete_one({"_id": oid(doc_id)})

    def count(self, query: Optional[dict] = None) -> int:
        return self.collection.count_documents(query or {})
