from app.domain.entities.partner import Partner
from app.domain.ports.repositories import PartnerRepository

class PartnerService:
    def __init__(self, repository: PartnerRepository) -> None: self._repository = repository
    async def list(self) -> list[Partner]: return await self._repository.find_all()
