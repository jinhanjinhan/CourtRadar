from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import db_session
from app.modules.users.schemas import UserCreate, UserRead
from app.modules.users.service import create_user, get_user
from app.schemas.common import CreatedResponse


router = APIRouter(prefix="", tags=["users"])


@router.post("/users", response_model=CreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_user_route(payload: UserCreate, session: AsyncSession = Depends(db_session)) -> CreatedResponse:
    try:
        user = await create_user(session, payload)
    except ValueError as exc:
        message = str(exc)
        if message == "email already exists":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc

    return CreatedResponse(id=user.id, created_at=user.created_at)


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user_route(user_id: int, session: AsyncSession = Depends(db_session)) -> UserRead:
    user = await get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    return UserRead.model_validate(user)
