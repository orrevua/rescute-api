from uuid import UUID

from app.domain.entities.cat import Cat
from app.domain.ports.repositories import CatRepository


class CatService:
    def __init__(self, cat_repo: CatRepository) -> None:
        self._cat_repo = cat_repo

    async def create_cat(self, protector_id: UUID, cat_data: dict) -> Cat:
        cat = Cat(protector_id=protector_id, **cat_data)
        return await self._cat_repo.save(cat)

    async def update_cat(self, protector_id: UUID, cat_id: UUID, cat_data: dict) -> Cat:
        cat = await self._cat_repo.find_by_id(cat_id)
        if not cat or cat.protector_id != protector_id:
            raise ValueError("Cat not found or not owned by this protector")
        for key, value in cat_data.items():
            if hasattr(cat, key):
                setattr(cat, key, value)
        return await self._cat_repo.save(cat)

    async def delete_cat(self, protector_id: UUID, cat_id: UUID) -> None:
        cat = await self._cat_repo.find_by_id(cat_id)
        if not cat or cat.protector_id != protector_id:
            raise ValueError("Cat not found or not owned by this protector")
        await self._cat_repo.delete(cat_id)

    async def list_cats(self, filters: dict) -> list[Cat]:
        return await self._cat_repo.find_all(filters)

    async def get_cat(self, cat_id: UUID) -> Cat:
        cat = await self._cat_repo.find_by_id(cat_id)
        if not cat:
            raise ValueError("Cat not found")
        return cat

    async def get_my_cats(self, protector_id: UUID) -> list[Cat]:
        return await self._cat_repo.find_by_protector(protector_id)
