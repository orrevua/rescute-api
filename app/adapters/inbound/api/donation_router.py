from fastapi import APIRouter, Depends, Query, status
from app.adapters.inbound.api.middleware.auth import get_protector
from app.adapters.inbound.api.schemas.donation import DonationCreate, DonationResponse
from app.application.donation_service import DonationService
from app.dependencies import get_donation_service
from app.domain.entities.user import User
from app.domain.value_objects import DonationType

router = APIRouter(prefix='/donations', tags=['donations'])
@router.get('', response_model=list[DonationResponse])
async def list_donations(type: DonationType | None = Query(default=None), service: DonationService = Depends(get_donation_service)) -> list[DonationResponse]: return [DonationResponse.model_validate(post) for post in await service.list({'type': type})]
@router.post('', response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
async def create_donation(body: DonationCreate, user: User = Depends(get_protector), service: DonationService = Depends(get_donation_service)) -> DonationResponse: return DonationResponse.model_validate(await service.create(user.id, body.model_dump()))
