from fastapi import APIRouter, Depends, HTTPException, status

from app.adapters.inbound.api.middleware.auth import get_current_user
from app.adapters.inbound.api.schemas.user import ProfileResponse, ProfileUpdate
from app.application.user_service import UserService
from app.dependencies import get_user_service
from app.domain.entities.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/profile", response_model=ProfileResponse)
async def get_my_profile(user: User = Depends(get_current_user), service: UserService = Depends(get_user_service)) -> ProfileResponse:
    try:
        return ProfileResponse.model_validate(await service.get_profile(user))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.patch("/me/profile", response_model=ProfileResponse)
async def update_my_profile(body: ProfileUpdate, user: User = Depends(get_current_user), service: UserService = Depends(get_user_service)) -> ProfileResponse:
    try:
        return ProfileResponse.model_validate(await service.update_profile(user, body.model_dump(exclude_unset=True)))
    except ValueError as error:
        code = status.HTTP_404_NOT_FOUND if "not found" in str(error).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(error)) from error
