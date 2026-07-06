import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.adapters.inbound.api.middleware.auth import get_protector
from app.adapters.inbound.api.schemas.donation import (
    ContributionCreate,
    ContributionResponse,
    DonationCreate,
    DonationResponse,
    DonationUpdate,
    IntentCreate,
    IntentResponse,
)
from app.application.donation_service import DonationService
from app.dependencies import get_donation_service
from app.domain.entities.user import User
from app.domain.value_objects import DonationType
from app.rate_limit import limiter

log = logging.getLogger(__name__)

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


@router.patch("/{donation_id}", response_model=DonationResponse)
async def update_donation(
    donation_id: UUID,
    body: DonationUpdate,
    user: User = Depends(get_protector),
    service: DonationService = Depends(get_donation_service),
) -> DonationResponse:
    try:
        updated = await service.update(user.id, donation_id, body.model_dump(exclude_unset=True))
    except ValueError as error:
        log.warning("Donation update failed for %s: %s", donation_id, error)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found") from error
    return DonationResponse.model_validate(updated)


@router.post("/{donation_id}/contribute", response_model=ContributionResponse)
@limiter.limit("10/minute")
async def contribute(
    request: Request,
    donation_id: UUID,
    body: ContributionCreate,
    service: DonationService = Depends(get_donation_service),
) -> ContributionResponse:
    try:
        updated = await service.contribute(donation_id, body.amount)
    except ValueError as error:
        log.warning("Contribution rejected for %s: %s", donation_id, error)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return ContributionResponse(
        donation_id=donation_id,
        donor_name=body.donor_name,
        amount=body.amount,
        new_total=updated.current_amount,
    )


@router.post("/{donation_id}/intent", response_model=IntentResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def submit_intent(
    request: Request,
    donation_id: UUID,
    body: IntentCreate,
    service: DonationService = Depends(get_donation_service),
) -> IntentResponse:
    try:
        intent = await service.submit_intent({
            "donation_id": donation_id,
            **body.model_dump(),
        })
    except ValueError as error:
        log.warning("Donation intent rejected for %s: %s", donation_id, error)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Campaign not found") from error
    return IntentResponse.model_validate(intent)


@router.get("/intents", response_model=list[IntentResponse])
async def list_intents(
    user: User = Depends(get_protector),
    service: DonationService = Depends(get_donation_service),
) -> list[IntentResponse]:
    intents = await service.list_intents(user.id)
    return [IntentResponse.model_validate(i) for i in intents]
