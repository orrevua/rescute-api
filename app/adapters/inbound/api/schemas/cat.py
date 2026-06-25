from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.value_objects import Sex


class CatCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age_months: int = Field(ge=0)
    sex: Sex
    city: str = Field(min_length=1)
    state: str = Field(min_length=2, max_length=2)
    fiv_status: bool = False
    felv_status: bool = False
    castrated: bool = False
    vaccinated: bool = False
    dewormed: bool = False
    health_needs: str | None = None
    sociability: int = Field(ge=1, le=5)
    energy: int = Field(ge=1, le=5)
    playfulness: int = Field(ge=1, le=5)
    personality: str | None = None
    backstory: str | None = None
    photos: list[str] = Field(default_factory=list)


class CatUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    age_months: int | None = Field(default=None, ge=0)
    sex: Sex | None = None
    city: str | None = Field(default=None, min_length=1)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    fiv_status: bool | None = None
    felv_status: bool | None = None
    castrated: bool | None = None
    vaccinated: bool | None = None
    dewormed: bool | None = None
    health_needs: str | None = None
    sociability: int | None = Field(default=None, ge=1, le=5)
    energy: int | None = Field(default=None, ge=1, le=5)
    playfulness: int | None = Field(default=None, ge=1, le=5)
    personality: str | None = None
    backstory: str | None = None
    photos: list[str] | None = None


class CatResponse(BaseModel):
    id: UUID
    protector_id: UUID
    name: str
    age_months: int
    sex: Sex
    city: str
    state: str
    fiv_status: bool
    felv_status: bool
    castrated: bool
    vaccinated: bool
    dewormed: bool
    health_needs: str | None
    sociability: int
    energy: int
    playfulness: int
    personality: str | None
    backstory: str | None
    photos: list[str]
    ready_for_adoption: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class CatListResponse(BaseModel):
    items: list[CatResponse]
    total: int
