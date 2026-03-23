from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.session import SessionDetail, SessionHistoryResponse, TrendResponse
from app.services import session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/history", response_model=SessionHistoryResponse)
async def get_session_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SessionHistoryResponse:
    return await session_service.list_sessions(db, candidate_id=current_user.id)


@router.get("/trends", response_model=TrendResponse)
async def get_score_trends(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrendResponse:
    return await session_service.get_score_trends(db, candidate_id=current_user.id)


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session_detail(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SessionDetail:
    return await session_service.get_session_detail(
        db, session_id=session_id, candidate_id=current_user.id
    )
