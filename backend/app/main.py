import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes import (
    admin,
    assessments,
    assist,
    auth,
    backup,
    benchmarking,
    canary,
    dashboard,
    detection,
    evidence,
    ledger,
    logs,
    organisations,
    probe,
    questions,
    regulatory,
    remediation,
    reports,
    scoring,
)
from app.core.config import get_settings
from app.core.mongo import ensure_indexes
from app.core.rate_limit import limiter
from app.core.storage import ensure_buckets
from app.services.canary_service import start_watcher_thread
from app.services.fabric_service import start_reconciliation_thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rri")

_DEFAULT_JWT_SECRET = "dev-secret-change-me"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.environment == "production" and settings.jwt_secret_key == _DEFAULT_JWT_SECRET:
        raise RuntimeError(
            "JWT_SECRET_KEY is still set to the insecure development default. "
            "Set a real secret before starting in ENVIRONMENT=production."
        )
    try:
        ensure_indexes()
        ensure_buckets()
        start_watcher_thread()
        start_reconciliation_thread()
        logger.info("RRI backend startup complete.")
    except Exception as exc:  # pragma: no cover
        logger.error("Startup initialization failed: %s", exc)
    yield


settings = get_settings()

app = FastAPI(
    title="RRI — Ransomware Readiness Index API",
    version="1.0.0",
    description="Ransomware-readiness self-assessment and assurance platform API.",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_and_audit(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-RRI-Response-Time-Ms"] = str(round((time.time() - start) * 1000, 2))
    return response


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.get("/health")
def health():
    return {"status": "ok", "service": "rri-backend"}


@app.get("/")
def root():
    return RedirectResponse(url="/docs")


app.include_router(auth.router)
app.include_router(organisations.router)
app.include_router(questions.router)
app.include_router(assessments.router)
app.include_router(evidence.router)
app.include_router(probe.router)
app.include_router(backup.router)
app.include_router(detection.router)
app.include_router(logs.router)
app.include_router(canary.router)
app.include_router(remediation.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(benchmarking.router)
app.include_router(ledger.router)
app.include_router(admin.router)
app.include_router(assist.router)
app.include_router(scoring.router)
app.include_router(regulatory.router)
