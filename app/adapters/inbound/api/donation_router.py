from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.adapters.inbound.api.middleware.auth import get_protector
from app.adapters.inbound.api.schemas.donation import (
    ContributionCreate,
    ContributionResponse,
    DonationCreate,
    DonationResponse,
)
from app.application.donation_service import DonationService
from app.dependencies import get_donation_service
from app.domain.entities.user import User
from app.domain.value_objects import DonationType

router = APIRouter(prefix="/donations", tags=["donations"])


@router.get("", response_model=list[DonationResponse])
async def list_donations(
    type: DonationType | None = Query(default=None),
    service: DonationService = Depends(get_donation_service),
) -> list[DonationResponse]:
    return [DonationResponse.model_validate(post) for post in await service.list({"type": type})]


@router.post("", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
async def create_donation(
    body: DonationCreate,
    user: User = Depends(get_protector),
    service: DonationService = Depends(get_donation_service),
) -> DonationResponse:
    return DonationResponse.model_validate(await service.create(user.id, body.model_dump()))


@router.post("/{donation_id}/contribute", response_model=ContributionResponse)
async def contribute(
    donation_id: UUID,
    body: ContributionCreate,
    service: DonationService = Depends(get_donation_service),
) -> ContributionResponse:
    try:
        updated = await service.contribute(donation_id, body.amount)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return ContributionResponse(
        donation_id=donation_id,
        donor_name=body.donor_name,
        amount=body.amount,
        new_total=updated.current_amount,
    )
