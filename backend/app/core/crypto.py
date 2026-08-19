"""Ed25519 signing/verification and the SHA-256 hash-chain primitives used by
the integrity ledger and the verification probe. This module never talks to
the network — key material is either supplied via env/config or persisted to
local files that are gitignored.
"""
import base64
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

from app.core.config import get_settings

_LEDGER_KEY_FILE = Path(__file__).resolve().parent.parent.parent / ".ledger_key.b64"
_PROBE_KEY_DIR = Path(__file__).resolve().parent.parent.parent / "probes" / "keys"
_PROBE_PRIVATE_KEY_FILE = _PROBE_KEY_DIR / "probe_private_key.b64"
_PROBE_PUBLIC_KEY_FILE = _PROBE_KEY_DIR / "probe_public_key.b64"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _generate_keypair_b64() -> tuple[str, str]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(priv_bytes).decode(), base64.b64encode(pub_bytes).decode()


def load_or_create_ledger_private_key() -> Ed25519PrivateKey:
    settings = get_settings()
    if settings.ledger_private_key_b64:
        raw = base64.b64decode(settings.ledger_private_key_b64)
        return Ed25519PrivateKey.from_private_bytes(raw)

    if _LEDGER_KEY_FILE.exists():
        raw = base64.b64decode(_LEDGER_KEY_FILE.read_text().strip())
        return Ed25519PrivateKey.from_private_bytes(raw)

    priv_b64, _ = _generate_keypair_b64()
    _LEDGER_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _LEDGER_KEY_FILE.write_text(priv_b64)
    raw = base64.b64decode(priv_b64)
    return Ed25519PrivateKey.from_private_bytes(raw)


def get_ledger_public_key_b64() -> str:
    private_key = load_or_create_ledger_private_key()
    pub_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(pub_bytes).decode()


def sign_ledger_record(record_hash_hex: str) -> str:
    private_key = load_or_create_ledger_private_key()
    signature = private_key.sign(bytes.fromhex(record_hash_hex))
    return base64.b64encode(signature).decode()


def verify_ledger_signature(record_hash_hex: str, signature_b64: str) -> bool:
    public_key_b64 = get_ledger_public_key_b64()
    try:
        public_key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64))
        public_key.verify(base64.b64decode(signature_b64), bytes.fromhex(record_hash_hex))
        return True
    except Exception:
        return False


def compute_record_hash(payload_hash_hex: str, prev_record_hash_hex: str) -> str:
    combined = (payload_hash_hex + prev_record_hash_hex).encode("utf-8")
    return sha256_hex(combined)


def get_probe_private_key_pem() -> str:
    """PEM (PKCS8) form of the probe private key, embedded into the
    downloadable probe scripts so they can shell out to `openssl pkeyutl` to
    sign their own output."""
    priv_b64, _ = load_or_create_probe_keypair()
    raw = base64.b64decode(priv_b64)
    private_key = Ed25519PrivateKey.from_private_bytes(raw)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pem.decode()


def load_or_create_probe_keypair() -> tuple[str, str]:
    """Returns (private_key_b64, public_key_b64) for the verification probe.

    The private key is bundled into the downloadable probe scripts so they can
    sign their own output; the public key is what the backend uses to verify
    incoming probe results. Persisted to disk so re-issued probe downloads
    keep working against results signed by earlier downloads.
    """
    if _PROBE_PRIVATE_KEY_FILE.exists() and _PROBE_PUBLIC_KEY_FILE.exists():
        return (
            _PROBE_PRIVATE_KEY_FILE.read_text().strip(),
            _PROBE_PUBLIC_KEY_FILE.read_text().strip(),
        )

    priv_b64, pub_b64 = _generate_keypair_b64()
    _PROBE_KEY_DIR.mkdir(parents=True, exist_ok=True)
    _PROBE_PRIVATE_KEY_FILE.write_text(priv_b64)
    _PROBE_PUBLIC_KEY_FILE.write_text(pub_b64)
    return priv_b64, pub_b64


def verify_probe_signature(payload_bytes: bytes, signature_b64: str, public_key_b64: str) -> bool:
    try:
        public_key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64))
        public_key.verify(base64.b64decode(signature_b64), payload_bytes)
        return True
    except Exception:
        return False
