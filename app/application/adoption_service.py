from uuid import UUID

from app.domain.entities.adoption import AdoptionApplication
from app.domain.ports.repositories import AdoptionRepository, CatRepository
from app.domain.value_objects import ApplicationStatus


class AdoptionService:
    def __init__(
        self,
        adoption_repo: AdoptionRepository,
        cat_repo: CatRepository,
    ) -> None:
        self._adoption_repo = adoption_repo
        self._cat_repo = cat_repo

    async def submit_application(self, application_data: dict) -> AdoptionApplication:
        if not application_data.get("accepted_terms"):
            raise ValueError("Terms must be accepted")
        cat = await self._cat_repo.find_by_id(application_data["cat_id"])
        if not cat:
            raise ValueError("Cat not found")
        return await self._adoption_repo.save(AdoptionApplication(**application_data))

    async def list_for_protector(self, protector_id: UUID) -> list[AdoptionApplication]:
        return await self._adoption_repo.find_by_protector_cats(protector_id)

    async def update_status(
        self,
        protector_id: UUID,
        application_id: UUID,
        status: ApplicationStatus,
    ) -> AdoptionApplication:
        applications = await self._adoption_repo.find_by_protector_cats(protector_id)
        application = next((item for item in applications if item.id == application_id), None)
        if not application:
            raise ValueError("Application not found")
        application.status = status
        return await self._adoption_repo.save(application)
