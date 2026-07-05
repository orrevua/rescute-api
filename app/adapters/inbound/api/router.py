from fastapi import APIRouter

from app.adapters.inbound.api.auth_router import router as auth_router
from app.adapters.inbound.api.adoption_router import router as adoption_router
from app.adapters.inbound.api.cat_router import router as cat_router
from app.adapters.inbound.api.foster_router import router as foster_router
from app.adapters.inbound.api.donation_router import router as donation_router
from app.adapters.inbound.api.partner_router import router as partner_router
from app.adapters.inbound.api.user_router import router as user_router
from app.adapters.inbound.api.ai_care_router import router as ai_care_router
from app.adapters.inbound.api.dashboard_router import router as dashboard_router
from app.adapters.inbound.api.upload_router import router as upload_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(adoption_router)
router.include_router(foster_router)
router.include_router(donation_router)
router.include_router(partner_router)
router.include_router(user_router)
router.include_router(ai_care_router)
router.include_router(cat_router)
router.include_router(dashboard_router)
router.include_router(upload_router)
