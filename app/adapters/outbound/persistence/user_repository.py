from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.adapters.outbound.persistence.models import (
    FosterProfileModel,
    ProtectorProfileModel,
    UserModel,
)
from app.domain.entities.user import FosterProfile, Host, ProtectorProfile, User
from app.domain.ports.repositories import UserRepository
from app.domain.value_objects import UserRole


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> User:
        if user.id is None:
            model = _to_model(user)
            self._session.add(model)
            await self._session.flush()
            return _to_domain(model)
        model = await self._session.merge(_to_model(user))
        await self._session.flush()
        return _to_domain(model)

    async def find_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email).options(
            joinedload(UserModel.protector_profile),
            joinedload(UserModel.foster_profile),
        )
        model = (await self._session.execute(stmt)).scalars().first()
        return _to_domain(model) if model else None

    async def find_by_id(self, id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == id).options(
            joinedload(UserModel.protector_profile),
            joinedload(UserModel.foster_profile),
        )
        model = (await self._session.execute(stmt)).scalars().first()
        return _to_domain(model) if model else None

    async def save_protector_profile(self, profile: ProtectorProfile) -> ProtectorProfile:
        model = ProtectorProfileModel(
            user_id=profile.user_id,
            org_name=profile.org_name,
            description=profile.description,
            phone=profile.phone,
            city=profile.city,
            state=profile.state,
        )
        self._session.add(model)
        await self._session.flush()
        return ProtectorProfile(
            id=model.id, user_id=model.user_id, org_name=model.org_name,
            description=model.description, phone=model.phone, city=model.city, state=model.state,
        )

    async def save_foster_profile(self, profile: FosterProfile) -> FosterProfile:
        model = FosterProfileModel(
            user_id=profile.user_id,
            full_name=profile.full_name,
            phone=profile.phone,
            city=profile.city,
            state=profile.state,
        )
        self._session.add(model)
        await self._session.flush()
        return FosterProfile(
            id=model.id, user_id=model.user_id, full_name=model.full_name,
            phone=model.phone, city=model.city, state=model.state,
        )

    async def find_protector_profile(self, user_id: UUID) -> ProtectorProfile | None:
        stmt = select(ProtectorProfileModel).where(ProtectorProfileModel.user_id == user_id)
        model = (await self._session.execute(stmt)).scalars().first()
        if not model:
            return None
        return ProtectorProfile(
            id=model.id, user_id=model.user_id, org_name=model.org_name,
            description=model.description, phone=model.phone, city=model.city, state=model.state,
        )

    async def find_foster_profile(self, user_id: UUID) -> FosterProfile | None:
        stmt = select(FosterProfileModel).where(FosterProfileModel.user_id == user_id)
        model = (await self._session.execute(stmt)).scalars().first()
        if not model:
            return None
        return FosterProfile(
            id=model.id, user_id=model.user_id, full_name=model.full_name,
            phone=model.phone, city=model.city, state=model.state,
        )

    async def update_protector_profile(self, profile: ProtectorProfile) -> ProtectorProfile:
        stmt = select(ProtectorProfileModel).where(ProtectorProfileModel.user_id == profile.user_id)
        model = (await self._session.execute(stmt)).scalars().first()
        if not model:
            raise ValueError("Protector profile not found")
        model.org_name = profile.org_name
        model.description = profile.description
        model.phone = profile.phone
        model.city = profile.city
        model.state = profile.state
        await self._session.flush()
        return ProtectorProfile(
            id=model.id, user_id=model.user_id, org_name=model.org_name,
            description=model.description, phone=model.phone, city=model.city, state=model.state,
        )

    async def update_foster_profile(self, profile: FosterProfile) -> FosterProfile:
        stmt = select(FosterProfileModel).where(FosterProfileModel.user_id == profile.user_id)
        model = (await self._session.execute(stmt)).scalars().first()
        if not model:
            raise ValueError("Foster profile not found")
        model.full_name = profile.full_name
        model.phone = profile.phone
        model.city = profile.city
        model.state = profile.state
        await self._session.flush()
        return FosterProfile(
            id=model.id, user_id=model.user_id, full_name=model.full_name,
            phone=model.phone, city=model.city, state=model.state,
        )

    async def find_hosts(self) -> list[Host]:
        protectors = (await self._session.execute(select(ProtectorProfileModel))).scalars().all()
        fosters = (await self._session.execute(select(FosterProfileModel))).scalars().all()
        hosts = [
            Host(user_id=p.user_id, role=UserRole.protector, display_name=p.org_name, city=p.city, state=p.state)
            for p in protectors
        ]
        hosts += [
            Host(user_id=f.user_id, role=UserRole.foster, display_name=f.full_name, city=f.city, state=f.state)
            for f in fosters
        ]
        return hosts


def _to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        hashed_password=model.hashed_password,
        role=UserRole(model.role),
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_model(user: User) -> UserModel:
    model = UserModel(
        id=user.id,
        email=user.email,
        hashed_password=user.hashed_password,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
    return model
