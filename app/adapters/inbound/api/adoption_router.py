from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from app.adapters.inbound.api.middleware.auth import get_protector
from app.adapters.inbound.api.schemas.adoption import (
    AdoptionCreate,
    AdoptionResponse,
    AdoptionStatusUpdate,
)
from app.application.adoption_service import AdoptionService
from app.dependencies import get_adoption_service
from app.domain.entities.user import User

router = APIRouter(prefix="/adoptions", tags=["adoptions"])

@router.post("", response_model=AdoptionResponse, status_code=status.HTTP_201_CREATED)
async def submit_adoption(
    body: AdoptionCreate,
    service: AdoptionService = Depends(get_adoption_service),
) -> AdoptionResponse:
    try:
        return AdoptionResponse.model_validate(
            await service.submit_application(body.model_dump())
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.get("", response_model=list[AdoptionResponse])
async def list_adoptions(
    user: User = Depends(get_protector),
    service: AdoptionService = Depends(get_adoption_service),
) -> list[AdoptionResponse]:
    applications = await service.list_for_protector(user.id)
    return [AdoptionResponse.model_validate(application) for application in applications]


@router.patch("/{application_id}/status", response_model=AdoptionResponse)
async def update_adoption_status(
    application_id: UUID,
    body: AdoptionStatusUpdate,
    user: User = Depends(get_protector),
    service: AdoptionService = Depends(get_adoption_service),
) -> AdoptionResponse:
    try:
        application = await service.update_status(user.id, application_id, body.status)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return AdoptionResponse.model_validate(application)
