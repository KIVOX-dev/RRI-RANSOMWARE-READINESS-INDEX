from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, get_current_user, require_platform_admin
from app.models.ledger import LedgerEntryOut, LedgerVerifyResult
from app.services import fabric_service, ledger_service

router = APIRouter(prefix="/ledger", tags=["ledger"])


@router.get("/entries", response_model=list[LedgerEntryOut])
def list_entries(user: CurrentUser = Depends(get_current_user)):
    return ledger_service.list_entries(user.organisation_id)


@router.get("/fabric-status")
def fabric_status(user: CurrentUser = Depends(get_current_user)):
    """Status of the optional Hyperledger Fabric anchor layer — read-only,
    never affects the hash chain's own verification result."""
    return fabric_service.get_chain_status()


@router.post("/verify", response_model=LedgerVerifyResult)
def verify(user: CurrentUser = Depends(get_current_user)):
    return ledger_service.verify_chain_and_process_approvals(user.organisation_id)


@router.post("/demo-tamper/{sequence}", response_model=LedgerEntryOut)
def demo_tamper(sequence: int, user: CurrentUser = Depends(require_platform_admin)):
    return ledger_service.demo_tamper(user.organisation_id, sequence)
