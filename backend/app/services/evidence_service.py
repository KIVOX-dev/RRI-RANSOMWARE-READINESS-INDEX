"""A3 — Evidence Upload. Real files land in MinIO; metadata + control
association lives in MongoDB. Evidence directly feeds the Assurance Score via
scoring_service (recomputed after every upload/delete)."""
import hashlib
import uuid

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.core.storage import ensure_buckets, presigned_get_url, put_object, remove_object
from app.repositories.collections import evidence_repo
from app.services import scoring_service

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "text/csv",
    "application/json",
}


def upload_evidence(assessment_id: str, organisation_id: str, control_id: str, uploaded_by: str, file: UploadFile) -> dict:
    settings = get_settings()
    ensure_buckets()

    content = file.file.read()
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    if len(content) > settings.max_evidence_size_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds maximum size")
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f"Unsupported file type: {file.content_type}")

    checksum = hashlib.sha256(content).hexdigest()
    safe_extension = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "bin"
    object_key = f"{organisation_id}/{assessment_id}/{control_id}/{uuid.uuid4().hex}.{safe_extension}"

    put_object(settings.minio_bucket_evidence, object_key, content, file.content_type)

    evidence_id = evidence_repo.insert(
        {
            "assessment_id": assessment_id,
            "organisation_id": organisation_id,
            "control_id": control_id,
            "filename": file.filename,
            "object_key": object_key,
            "mime_type": file.content_type,
            "size": len(content),
            "checksum": checksum,
            "uploaded_by": uploaded_by,
            "verification_status": "pending",
        }
    )

    scoring_service.recompute_assessment_scores(assessment_id)
    return evidence_repo.get_by_id(evidence_id)


def list_evidence(assessment_id: str) -> list[dict]:
    settings = get_settings()
    docs = evidence_repo.find({"assessment_id": assessment_id})
    for doc in docs:
        doc["download_url"] = presigned_get_url(settings.minio_bucket_evidence, doc["object_key"])
    return docs


def set_verification_status(evidence_id: str, status_value: str) -> dict:
    evidence = evidence_repo.get_by_id(evidence_id)
    if not evidence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
    evidence_repo.update_by_id(evidence_id, {"verification_status": status_value})
    scoring_service.recompute_assessment_scores(evidence["assessment_id"])
    return evidence_repo.get_by_id(evidence_id)


def delete_evidence(evidence_id: str) -> None:
    settings = get_settings()
    evidence = evidence_repo.get_by_id(evidence_id)
    if not evidence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
    remove_object(settings.minio_bucket_evidence, evidence["object_key"])
    evidence_repo.delete_by_id(evidence_id)
    scoring_service.recompute_assessment_scores(evidence["assessment_id"])
