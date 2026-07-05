from pydantic import BaseModel, ConfigDict

from app.domain.value_objects import UserRole


class ProfileResponse(BaseModel):
    email: str
    role: UserRole
    org_name: str | None = None
    full_name: str | None = None
    description: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    org_name: str | None = None
    full_name: str | None = None
    description: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
