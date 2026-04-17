from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.schemas.coach import CoachScoreRequest
from app.schemas.session import QuestionResult, SessionHistoryResponse
from app.services import coach_service

router = APIRouter(tags=["coach"])


def _require_coach(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Dependency that enforces coach or admin role."""
    if current_user.role not in (UserRole.coach, UserRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Coach role required",
        )
    return current_user


@router.post(
    "/sessions/{session_id}/questions/{question_id}/score",
    response_model=QuestionResult,
)
async def submit_coach_score(
    session_id: UUID,
    question_id: UUID,
    body: CoachScoreRequest,
    current_user: Annotated[User, Depends(_require_coach)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QuestionResult:
    try:
        return await coach_service.submit_coach_score(
            db,
            session_id=session_id,
            question_id=question_id,
            coach_id=current_user.id,
            scores=body.scores,
            justification=body.justification,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit coach score.",
        )


@router.get("/sessions", response_model=SessionHistoryResponse)
async def get_sessions_for_review(
    current_user: Annotated[User, Depends(_require_coach)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SessionHistoryResponse:
    return await coach_service.list_sessions_for_review(db)
