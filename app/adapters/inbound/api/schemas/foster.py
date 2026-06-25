from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.value_objects import ApplicationStatus


class FosterApplicationCreate(BaseModel):
    existing_pets: str = Field(min_length=1, max_length=2000)
    compatibility: str = Field(min_length=1, max_length=2000)
    prior_experience: str = Field(min_length=1, max_length=2000)
    city: str = Field(min_length=1, max_length=100)
    cost_aware: bool


class FosterApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class FosterApplicationResponse(BaseModel):
    id: UUID
    user_id: UUID
    existing_pets: str
    compatibility: str
    prior_experience: str
    city: str
    cost_aware: bool
    status: ApplicationStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
