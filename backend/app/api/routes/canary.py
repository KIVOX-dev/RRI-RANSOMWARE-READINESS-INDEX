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
    return canary_service.simulate_touch(canary_id)


@router.get("/stream")
async def stream(token: str = Query(...)):
    """SSE stream of live canary events for the caller's organisation. Token
    is passed as a query param since EventSource cannot set headers."""
    payload = decode_access_token(token)
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
