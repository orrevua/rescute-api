from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.value_objects import ApplicationStatus


class AdoptionCreate(BaseModel):
    cat_id: UUID
    applicant_name: str = Field(min_length=1, max_length=100)
    applicant_email: EmailStr
    applicant_phone: str = Field(min_length=8, max_length=30)
    message: str | None = Field(default=None, max_length=2000)
    accepted_terms: bool


class AdoptionStatusUpdate(BaseModel):
    status: ApplicationStatus


class AdoptionResponse(BaseModel):
    id: UUID
    cat_id: UUID
    applicant_name: str
    applicant_email: EmailStr
    applicant_phone: str
    message: str | None
    accepted_terms: bool
    status: ApplicationStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
