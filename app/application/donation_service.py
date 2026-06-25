from uuid import UUID

from app.domain.entities.donation import DonationIntent, DonationPost
from app.domain.ports.repositories import DonationPostRepository


class DonationService:
    def __init__(self, donation_repo: DonationPostRepository) -> None:
        self._donation_repo = donation_repo

    async def create(self, protector_id: UUID, data: dict) -> DonationPost:
        return await self._donation_repo.save(DonationPost(protector_id=protector_id, **data))

    async def list(self, filters: dict) -> list[DonationPost]:
        return await self._donation_repo.find_all(filters)

    async def contribute(self, donation_id: UUID, amount: float) -> DonationPost:
        post = await self._donation_repo.find_by_id(donation_id)
        if not post:
            raise ValueError("Campaign not found")
        if not post.is_active:
            raise ValueError("Campaign is no longer active")
        post.current_amount += amount
        return await self._donation_repo.save(post)

    async def submit_intent(self, intent_data: dict) -> DonationIntent:
        donation_id = intent_data["donation_id"]
        post = await self._donation_repo.find_by_id(donation_id)
        if not post:
            raise ValueError("Campaign not found")
        intent = DonationIntent(**intent_data)
        return await self._donation_repo.save_intent(intent)

    async def list_intents(self, protector_id: UUID) -> list[DonationIntent]:
        return await self._donation_repo.find_intents_by_protector(protector_id)
