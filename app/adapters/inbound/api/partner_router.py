from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.adapters.inbound.api.middleware.auth import get_current_user
from app.adapters.inbound.api.schemas.partner import (
    HostResponse,
    NegotiationAction,
    NegotiationResponse,
    PartnerRegister,
    PartnerResponse,
    PartnerUpdate,
)
from app.application.partner_service import PartnerService
from app.dependencies import get_partner_repository, get_partner_service
from app.domain.entities.partner import PartnerNegotiation
from app.domain.entities.user import User
from app.domain.ports.repositories import PartnerRepository

router = APIRouter(prefix="/partners", tags=["partners"])


@router.get("", response_model=list[PartnerResponse])
async def list_partners(service: PartnerService = Depends(get_partner_service)) -> list[PartnerResponse]:
    return [PartnerResponse.model_validate(partner) for partner in await service.list()]


@router.get("/hosts", response_model=list[HostResponse])
async def list_hosts(service: PartnerService = Depends(get_partner_service)) -> list[HostResponse]:
    return [HostResponse.model_validate(host) for host in await service.list_hosts()]


@router.post("/register", response_model=NegotiationResponse, status_code=status.HTTP_201_CREATED)
async def register_partner(body: PartnerRegister, service: PartnerService = Depends(get_partner_service), repository: PartnerRepository = Depends(get_partner_repository)) -> NegotiationResponse:
    return await _negotiation_response(await service.register(body.model_dump()), repository)


@router.get("/negotiations", response_model=list[NegotiationResponse])
async def list_negotiations(user: User = Depends(get_current_user), service: PartnerService = Depends(get_partner_service), repository: PartnerRepository = Depends(get_partner_repository)) -> list[NegotiationResponse]:
    return [await _negotiation_response(n, repository) for n in await service.list_negotiations(user.id)]


@router.patch("/negotiations/{negotiation_id}", response_model=NegotiationResponse)
async def act_on_negotiation(negotiation_id: UUID, body: NegotiationAction, user: User = Depends(get_current_user), service: PartnerService = Depends(get_partner_service), repository: PartnerRepository = Depends(get_partner_repository)) -> NegotiationResponse:
    try:
        negotiation = await service.act_on_negotiation(user.id, negotiation_id, body.action, body.counter_amount, body.counter_message)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return await _negotiation_response(negotiation, repository)


@router.patch("/{partner_id}", response_model=PartnerResponse)
async def update_partner(partner_id: UUID, body: PartnerUpdate, user: User = Depends(get_current_user), service: PartnerService = Depends(get_partner_service)) -> PartnerResponse:
    try:
        return PartnerResponse.model_validate(await service.update_partner(user.id, partner_id, body.model_dump(exclude_unset=True)))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/{partner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_partner(partner_id: UUID, user: User = Depends(get_current_user), service: PartnerService = Depends(get_partner_service)) -> None:
    try:
        await service.delete_partner(user.id, partner_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


async def _negotiation_response(negotiation: PartnerNegotiation, repository: PartnerRepository) -> NegotiationResponse:
    partner = await repository.find_by_id(negotiation.partner_id)
    return NegotiationResponse(
        id=negotiation.id,
        status=negotiation.status,
        proposed_amount=negotiation.proposed_amount,
        proposed_message=negotiation.proposed_message,
        contact_email=negotiation.contact_email,
        contact_phone=negotiation.contact_phone,
        counter_amount=negotiation.counter_amount,
        counter_message=negotiation.counter_message,
        created_at=negotiation.created_at,
        partner=PartnerResponse.model_validate(partner),
    )
