from uuid import UUID

from app.domain.entities.foster import FosterApplication
from app.domain.ports.repositories import FosterApplicationRepository
from app.domain.value_objects import ApplicationStatus


class FosterService:
    def __init__(self, foster_repo: FosterApplicationRepository) -> None:
        self._foster_repo = foster_repo

    async def submit_application(
        self,
        user_id: UUID,
        application_data: dict,
    ) -> FosterApplication:
        return await self._foster_repo.save(
            FosterApplication(user_id=user_id, **application_data)
        )

    async def list_own(self, user_id: UUID) -> list[FosterApplication]:
        return await self._foster_repo.find_by_user(user_id)

    async def list_all(self) -> list[FosterApplication]:
        return await self._foster_repo.find_all()

    async def update_status(
        self,
        application_id: UUID,
        status: ApplicationStatus,
    ) -> FosterApplication:
        application = await self._foster_repo.find_by_id(application_id)
        if not application:
            raise ValueError("Application not found")
        application.status = status
        return await self._foster_repo.save(application)
