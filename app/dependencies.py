"""Central dependency injection registry for FastAPI."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.persistence.cat_repository import CatRepositoryImpl
from app.adapters.outbound.persistence.adoption_repository import AdoptionRepositoryImpl
from app.adapters.outbound.persistence.foster_repository import FosterRepositoryImpl
from app.adapters.outbound.persistence.donation_repository import DonationPostRepositoryImpl
from app.adapters.outbound.persistence.partner_repository import PartnerRepositoryImpl
from app.adapters.outbound.persistence.database import get_session
from app.adapters.outbound.persistence.user_repository import UserRepositoryImpl
from app.application.auth_service import AuthService
from app.application.adoption_service import AdoptionService
from app.application.foster_service import FosterService
from app.application.donation_service import DonationService
from app.application.partner_service import PartnerService
from app.application.ai_care_service import AICareService
from app.adapters.outbound.ai.openai_provider import OpenAICompatibleProvider
from app.application.cat_service import CatService
from app.domain.ports.repositories import AdoptionRepository, CatRepository, DonationPostRepository, FosterApplicationRepository, PartnerRepository, UserRepository


async def get_db(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[AsyncSession, None]:
    yield session


def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepositoryImpl(session)

def get_cat_repository(session: AsyncSession = Depends(get_session)) -> CatRepository:
    return CatRepositoryImpl(session)


def get_adoption_repository(
    session: AsyncSession = Depends(get_session),
) -> AdoptionRepository:
    return AdoptionRepositoryImpl(session)


def get_foster_repository(
    session: AsyncSession = Depends(get_session),
) -> FosterApplicationRepository:
    return FosterRepositoryImpl(session)


def get_donation_repository(
    session: AsyncSession = Depends(get_session),
) -> DonationPostRepository:
    return DonationPostRepositoryImpl(session)

def get_partner_repository(session: AsyncSession = Depends(get_session)) -> PartnerRepository:
    return PartnerRepositoryImpl(session)

def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository)


def get_cat_service(
    repository: CatRepository = Depends(get_cat_repository),
) -> CatService:
    return CatService(repository)


def get_adoption_service(
    adoption_repository: AdoptionRepository = Depends(get_adoption_repository),
    cat_repository: CatRepository = Depends(get_cat_repository),
) -> AdoptionService:
    return AdoptionService(adoption_repository, cat_repository)


def get_foster_service(
    repository: FosterApplicationRepository = Depends(get_foster_repository),
) -> FosterService:
    return FosterService(repository)


def get_donation_service(
    repository: DonationPostRepository = Depends(get_donation_repository),
) -> DonationService:
    return DonationService(repository)

def get_partner_service(repository: PartnerRepository = Depends(get_partner_repository)) -> PartnerService:
    return PartnerService(repository)

def get_ai_care_service() -> AICareService:
    return AICareService(OpenAICompatibleProvider())
