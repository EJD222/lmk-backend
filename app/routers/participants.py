from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.middleware.rate_limit import limiter
from app.schemas.base import APIResponse
from app.schemas.participant import JoinSessionRequest
from app.services.participant_service import ParticipantService

router = APIRouter(prefix="/sessions/{link_id}/participants", tags=["participants"])


@router.post("/", response_model=APIResponse)
@limiter.limit("20/minute")
async def join_session_by_link_id(
    request: Request,
    link_id: str,
    body: JoinSessionRequest,
    db: Session = Depends(get_db),
):
    data = ParticipantService.join_by_link_id(db, link_id, body)
    return APIResponse(success=True, data=data.model_dump())
