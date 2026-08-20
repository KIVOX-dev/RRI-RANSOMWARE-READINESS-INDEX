import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sse_starlette.sse import EventSourceResponse

from app.api.deps import CurrentUser, get_current_user
from app.core.cache import get_redis
from app.core.security import create_access_token, decode_access_token
from app.models.canary import CanaryDeploySettings
from app.services import canary_service

router = APIRouter(prefix="/canary", tags=["canary"])


@router.post("/deploy")
def deploy(settings_in: CanaryDeploySettings, assessment_id: str | None = None, user: CurrentUser = Depends(get_current_user)):
    return canary_service.deploy_canaries(user.organisation_id, assessment_id, settings_in.canary_count)


@router.get("")
def list_canaries(user: CurrentUser = Depends(get_current_user)):
    return canary_service.list_canaries(user.organisation_id)


@router.get("/events")
def list_events(user: CurrentUser = Depends(get_current_user)):
    return canary_service.list_events(user.organisation_id)


@router.post("/simulate/{canary_id}")
def simulate(canary_id: str, user: CurrentUser = Depends(get_current_user)):
    return canary_service.simulate_touch(canary_id, user.organisation_id)


@router.get("/stream-token")
def stream_token(user: CurrentUser = Depends(get_current_user)):
    """Mints a short-lived, single-purpose token for the SSE stream below.
    EventSource can't set an Authorization header, so the token has to travel
    in the URL — keeping it short-lived (unlike the normal session token)
    limits how long a copy leaked into browser history / access logs stays
    useful if it's ever captured."""
    token = create_access_token(
        user.id,
        {"organisation_id": user.organisation_id, "scope": "canary_stream"},
        expires_minutes=5,
    )
    return {"token": token}


@router.get("/stream")
async def stream(token: str = Query(...)):
    """SSE stream of live canary events for the caller's organisation. Token
    is passed as a query param since EventSource cannot set headers."""
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    organisation_id = payload.get("organisation_id", "")

    async def event_generator():
        redis_client = get_redis()
        pubsub = redis_client.pubsub()
        pubsub.subscribe(f"canary_events:{organisation_id}")
        try:
            while True:
                message = pubsub.get_message(timeout=1.0)
                if message and message["type"] == "message":
                    yield {"event": "canary_event", "data": message["data"]}
                await asyncio.sleep(0.5)
        finally:
            pubsub.close()

    return EventSourceResponse(event_generator())
