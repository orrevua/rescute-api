from __future__ import annotations

from app.domain.entities.user import FosterProfile, ProtectorProfile, User, UserProfile
from app.domain.ports.repositories import UserRepository
from app.domain.value_objects import UserRole

_PROTECTOR_FIELDS = ("org_name", "description", "phone", "city", "state")
_PROTECTOR_REQUIRED = ("org_name",)
_FOSTER_FIELDS = ("full_name", "phone", "city", "state")
_FOSTER_REQUIRED = ("full_name", "phone", "city", "state")


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def get_profile(self, user: User) -> UserProfile:
        if user.role == UserRole.protector:
            return _to_protector_profile(user, await self._load_protector(user))
        return _to_foster_profile(user, await self._load_foster(user))

    async def update_profile(self, user: User, data: dict) -> UserProfile:
        if user.role == UserRole.protector:
            profile = await self._load_protector(user)
            _apply(profile, data, _PROTECTOR_FIELDS, _PROTECTOR_REQUIRED)
            return _to_protector_profile(user, await self._user_repo.update_protector_profile(profile))
        profile = await self._load_foster(user)
        _apply(profile, data, _FOSTER_FIELDS, _FOSTER_REQUIRED)
        return _to_foster_profile(user, await self._user_repo.update_foster_profile(profile))

    async def _load_protector(self, user: User) -> ProtectorProfile:
        profile = await self._user_repo.find_protector_profile(user.id)
        if not profile:
            raise ValueError("Profile not found")
        return profile

    async def _load_foster(self, user: User) -> FosterProfile:
        profile = await self._user_repo.find_foster_profile(user.id)
        if not profile:
            raise ValueError("Profile not found")
        return profile


def _apply(profile: object, data: dict, fields: tuple[str, ...], required: tuple[str, ...]) -> None:
    for key in fields:
        if key not in data or data[key] is None:
            continue
        value = data[key]
        if key in required and not str(value).strip():
            raise ValueError(f"{key} cannot be blank")
        setattr(profile, key, value)


def _to_protector_profile(user: User, profile: ProtectorProfile) -> UserProfile:
    return UserProfile(
        email=user.email, role=user.role, org_name=profile.org_name,
        description=profile.description, phone=profile.phone, city=profile.city, state=profile.state,
    )


def _to_foster_profile(user: User, profile: FosterProfile) -> UserProfile:
    return UserProfile(
        email=user.email, role=user.role, full_name=profile.full_name,
        phone=profile.phone, city=profile.city, state=profile.state,
    )
