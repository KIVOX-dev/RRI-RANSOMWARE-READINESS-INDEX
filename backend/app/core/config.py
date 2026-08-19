from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "rri"

    redis_url: str = "redis://localhost:6379/0"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "rri_minio_admin"
    minio_secret_key: str = "rri_minio_secret_change_me"
    minio_bucket_evidence: str = "rri-evidence"
    minio_bucket_reports: str = "rri-reports"
    minio_secure: bool = False
    # Host:port the *browser* can reach MinIO at, for presigned download
    # links — different from minio_endpoint, which is the internal Docker
    # network address the backend itself uses to talk to MinIO.
    minio_public_endpoint: str = "localhost:9000"
    minio_public_secure: bool = False

    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480

    frontend_origin: str = "http://localhost:5173"
    public_backend_url: str = "http://localhost:8000"  # what the probe scripts / browser should call

    ledger_private_key_b64: str = ""

    openrouter_api_keys: str = ""
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct:free"
    openrouter_fallback_models: str = ""

    max_evidence_size_bytes: int = 25 * 1024 * 1024

    # Optional Hyperledger Fabric stretch anchor for the Integrity Ledger.
    # The application's *default* integrity mechanism is the signed hash
    # chain in ledger_service.py, which works with or without this. This
    # talks to a local fabric-gateway-api sidecar (see backend/app/services/
    # fabric_service.py for why) fronting a single-org Fabric network — not
    # a public blockchain.
    fabric_enabled: bool = True
    fabric_gateway_url: str = "http://fabric-gateway-api:3001"

    @property
    def openrouter_keys_list(self) -> list[str]:
        return [k.strip() for k in self.openrouter_api_keys.split(",") if k.strip()]

    @property
    def openrouter_models_list(self) -> list[str]:
        models = [self.openrouter_model] + [
            m.strip() for m in self.openrouter_fallback_models.split(",") if m.strip()
        ]
        seen = set()
        ordered = []
        for m in models:
            if m not in seen:
                seen.add(m)
                ordered.append(m)
        return ordered


@lru_cache
def get_settings() -> Settings:
    return Settings()
