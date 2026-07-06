from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.value_objects import UserRole


@dataclass
class User:
    email: str
    hashed_password: str
    role: UserRole
    id: UUID | None = None
    is_active: bool = True
    token_version: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ProtectorProfile:
    user_id: UUID
    org_name: str
    id: UUID | None = None
    description: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None


@dataclass
class FosterProfile:
    user_id: UUID
    full_name: str
    phone: str
    city: str
    state: str
    id: UUID | None = None


@dataclass
class Host:
    user_id: UUID
    role: UserRole
    display_name: str
    city: str | None = None
    state: str | None = None


@dataclass
class UserProfile:
    email: str
    role: UserRole
    org_name: str | None = None
    full_name: str | None = None
    description: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
