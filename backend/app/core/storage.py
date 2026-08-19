import io
from functools import lru_cache

import urllib3
from minio import Minio

from app.core.config import get_settings


def _fast_fail_http_client() -> urllib3.PoolManager:
    # No retries / short timeout: if object storage is unreachable we want a
    # fast, clear failure rather than ~10s of exponential-backoff retries
    # blocking app startup or a request.
    return urllib3.PoolManager(
        timeout=urllib3.Timeout(connect=2.0, read=5.0),
        retries=urllib3.Retry(total=0),
    )


@lru_cache
def get_minio_client() -> Minio:
    """The operational client, used for everything the backend itself does
    (upload, bucket checks, delete). Points at MinIO's address *inside* the
    Docker network."""
    settings = get_settings()
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
        http_client=_fast_fail_http_client(),
    )


@lru_cache
def get_minio_public_client() -> Minio:
    """Used only to *generate* presigned URLs. Those URLs are handed to the
    browser, which is outside the Docker network and can't resolve the
    internal "minio" hostname — this client signs against the
    externally-reachable host:port instead, so the resulting link actually
    works when clicked.

    `region` is pinned explicitly: without it, minio-py's presigned-URL path
    makes a live lookup call to the endpoint to discover the bucket's region
    before it will sign anything — and "localhost:9000" from *inside* this
    container means the container itself, not the host's MinIO port, so that
    lookup fails even though the endpoint is only ever used to build a URL
    string here, never to actually connect.
    """
    settings = get_settings()
    return Minio(
        settings.minio_public_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_public_secure,
        region="us-east-1",
        http_client=_fast_fail_http_client(),
    )


def ensure_buckets() -> None:
    settings = get_settings()
    client = get_minio_client()
    for bucket in (settings.minio_bucket_evidence, settings.minio_bucket_reports):
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)


def put_object(bucket: str, object_key: str, data: bytes, content_type: str) -> None:
    client = get_minio_client()
    client.put_object(
        bucket,
        object_key,
        data=io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )


def get_object_bytes(bucket: str, object_key: str) -> bytes:
    client = get_minio_client()
    response = client.get_object(bucket, object_key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def presigned_get_url(bucket: str, object_key: str, expires_seconds: int = 3600):
    from datetime import timedelta

    client = get_minio_public_client()
    return client.presigned_get_object(bucket, object_key, expires=timedelta(seconds=expires_seconds))


def remove_object(bucket: str, object_key: str) -> None:
    client = get_minio_client()
    client.remove_object(bucket, object_key)
