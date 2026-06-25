from fastapi import APIRouter, Depends
from app.adapters.inbound.api.schemas.partner import PartnerResponse
from app.application.partner_service import PartnerService
from app.dependencies import get_partner_service
router = APIRouter(prefix='/partners', tags=['partners'])
@router.get('', response_model=list[PartnerResponse])
async def list_partners(service: PartnerService = Depends(get_partner_service)) -> list[PartnerResponse]: return [PartnerResponse.model_validate(partner) for partner in await service.list()]
