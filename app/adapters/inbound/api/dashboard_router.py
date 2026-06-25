from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.adapters.inbound.api.middleware.auth import get_protector
from app.application.cat_service import CatService
from app.application.adoption_service import AdoptionService
from app.application.donation_service import DonationService
from app.dependencies import get_cat_service, get_adoption_service, get_donation_service
from app.domain.entities.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardStats(BaseModel):
    cat_count: int
    application_count: int
    active_campaign_count: int


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    user: User = Depends(get_protector),
    cat_service: CatService = Depends(get_cat_service),
    adoption_service: AdoptionService = Depends(get_adoption_service),
    donation_service: DonationService = Depends(get_donation_service),
) -> DashboardStats:
    cats = await cat_service.get_my_cats(user.id)
    applications = await adoption_service.list_for_protector(user.id)
    donations = await donation_service.list({"type": None})
    active_campaigns = [d for d in donations if d.protector_id == user.id and d.is_active]
    return DashboardStats(
        cat_count=len(cats),
        application_count=len(applications),
        active_campaign_count=len(active_campaigns),
    )
