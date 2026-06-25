from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from app.adapters.inbound.api.middleware.auth import get_current_user, get_protector
from app.adapters.inbound.api.schemas.foster import FosterApplicationCreate, FosterApplicationResponse, FosterApplicationStatusUpdate
from app.application.foster_service import FosterService
from app.dependencies import get_foster_service
from app.domain.entities.user import User
from app.domain.value_objects import UserRole

router = APIRouter(prefix="/foster/applications", tags=["foster"])

@router.post("", response_model=FosterApplicationResponse, status_code=status.HTTP_201_CREATED)
async def submit_foster_application(body: FosterApplicationCreate, user: User = Depends(get_current_user), service: FosterService = Depends(get_foster_service)) -> FosterApplicationResponse:
    if user.role is not UserRole.foster:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Foster role required")
    return FosterApplicationResponse.model_validate(await service.submit_application(user.id, body.model_dump()))


@router.get("", response_model=list[FosterApplicationResponse])
async def list_foster_applications(user: User = Depends(get_current_user), service: FosterService = Depends(get_foster_service)) -> list[FosterApplicationResponse]:
    applications = await (service.list_own(user.id) if user.role is UserRole.foster else service.list_all())
    return [FosterApplicationResponse.model_validate(application) for application in applications]


@router.patch("/{application_id}/status", response_model=FosterApplicationResponse)
async def update_foster_status(application_id: UUID, body: FosterApplicationStatusUpdate, user: User = Depends(get_protector), service: FosterService = Depends(get_foster_service)) -> FosterApplicationResponse:
    try:
        return FosterApplicationResponse.model_validate(await service.update_status(application_id, body.status))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
