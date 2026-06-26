from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.persistence.models import PartnerModel
from app.domain.entities.partner import Partner
from app.domain.ports.repositories import PartnerRepository


class PartnerRepositoryImpl(PartnerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, partner: Partner) -> Partner:
        model = _to_model(partner) if partner.id is None else await self._session.merge(_to_model(partner))
        if partner.id is None:
            self._session.add(model)
        await self._session.flush()
        return _to_domain(model)

    async def find_all(self) -> list[Partner]:
        models = (
            await self._session.execute(
                select(PartnerModel).where(PartnerModel.is_active.is_(True))
            )
        ).scalars().all()
        return [_to_domain(model) for model in models]

    async def find_by_location(self, lat: float, lng: float, radius: float) -> list[Partner]:
        return await self.find_all()


def _to_domain(model: PartnerModel) -> Partner:
    return Partner(
        id=model.id,
        name=model.name,
        description=model.description,
        address=model.address,
        cep=model.cep,
        city=model.city,
        state=model.state,
        lat=model.lat,
        lng=model.lng,
        coupon_code=model.coupon_code,
        discount_pct=model.discount_pct,
        is_active=model.is_active,
    )


def _to_model(partner: Partner) -> PartnerModel:
    return PartnerModel(
        id=partner.id,
        name=partner.name,
        description=partner.description,
        address=partner.address,
        cep=partner.cep,
        city=partner.city,
        state=partner.state,
        lat=partner.lat,
        lng=partner.lng,
        coupon_code=partner.coupon_code,
        discount_pct=partner.discount_pct,
        is_active=partner.is_active,
    )
