from __future__ import annotations

from uuid import UUID

from app.domain.entities.partner import Partner, PartnerNegotiation
from app.domain.entities.user import Host
from app.domain.ports.repositories import PartnerRepository, UserRepository
from app.domain.value_objects import NegotiationStatus


class PartnerService:
    def __init__(self, repository: PartnerRepository, user_repository: UserRepository) -> None:
        self._repository = repository
        self._user_repository = user_repository

    async def list(self) -> list[Partner]:
        return await self._repository.find_all()

    async def list_hosts(self) -> list[Host]:
        return await self._user_repository.find_hosts()

    async def register(self, data: dict) -> PartnerNegotiation:
        partner = await self._repository.save(
            Partner(
                name=data["name"],
                description=data.get("description"),
                address=data["address"],
                cep=data["cep"],
                city=data["city"],
                state=data["state"],
                coupon_code=data.get("coupon_code"),
                discount_pct=data.get("discount_pct"),
                is_active=False,
            )
        )
        return await self._repository.save_negotiation(
            PartnerNegotiation(
                partner_id=partner.id,
                host_id=data["host_id"],
                proposed_amount=data["proposed_amount"],
                proposed_message=data.get("proposed_message"),
                contact_email=data["contact_email"],
                contact_phone=data["contact_phone"],
            )
        )

    async def list_negotiations(self, host_id: UUID) -> list[PartnerNegotiation]:
        return await self._repository.find_negotiations_by_host(host_id)

    async def act_on_negotiation(
        self,
        host_id: UUID,
        negotiation_id: UUID,
        action: str,
        counter_amount: float | None = None,
        counter_message: str | None = None,
    ) -> PartnerNegotiation:
        negotiation = await self._repository.find_negotiation_by_id(negotiation_id)
        if not negotiation or negotiation.host_id != host_id:
            raise ValueError("Negotiation not found or not owned by this host")
        if action == "accept":
            negotiation.status = NegotiationStatus.accepted
            partner = await self._repository.find_by_id(negotiation.partner_id)
            if not partner:
                raise ValueError("Partner not found")
            partner.owner_id = host_id
            partner.is_active = True
            await self._repository.save(partner)
        elif action == "reject":
            negotiation.status = NegotiationStatus.rejected
        elif action == "counter":
            negotiation.status = NegotiationStatus.countered
            negotiation.counter_amount = counter_amount
            negotiation.counter_message = counter_message
        else:
            raise ValueError("Invalid negotiation action")
        return await self._repository.save_negotiation(negotiation)

    async def update_partner(self, owner_id: UUID, partner_id: UUID, data: dict) -> Partner:
        partner = await self._repository.find_by_id(partner_id)
        if not partner or partner.owner_id != owner_id:
            raise ValueError("Partner not found or not owned by this user")
        for key, value in data.items():
            if hasattr(partner, key):
                setattr(partner, key, value)
        return await self._repository.save(partner)

    async def delete_partner(self, owner_id: UUID, partner_id: UUID) -> None:
        partner = await self._repository.find_by_id(partner_id)
        if not partner or partner.owner_id != owner_id:
            raise ValueError("Partner not found or not owned by this user")
        await self._repository.delete(partner_id)
