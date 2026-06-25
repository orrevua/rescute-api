from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.value_objects import DonationType


class DonationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=140)
    description: str = Field(min_length=1, max_length=2000)
    type: DonationType
    target_amount: float | None = Field(default=None, gt=0)
    payment_link: str | None = Field(default=None, max_length=500)


class DonationResponse(BaseModel):
    id: UUID
    protector_id: UUID
    title: str
    description: str
    type: DonationType
    target_amount: float | None
    current_amount: float
    payment_link: str | None
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DonationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=140)
    description: str | None = Field(default=None, min_length=1, max_length=2000)
    target_amount: float | None = Field(default=None, gt=0)
    payment_link: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class ContributionCreate(BaseModel):
    donor_name: str = Field(min_length=1, max_length=200)
    donor_email: str = Field(min_length=3, max_length=200)
    amount: float = Field(gt=0)
    message: str | None = Field(default=None, max_length=500)


class ContributionResponse(BaseModel):
    donation_id: UUID
    donor_name: str
    amount: float
    new_total: float


class IntentCreate(BaseModel):
    donor_name: str = Field(min_length=1, max_length=200)
    donor_email: str = Field(min_length=3, max_length=200)
    donor_phone: str = Field(min_length=5, max_length=30)
    amount: float = Field(gt=0)
    message: str | None = Field(default=None, max_length=500)


class IntentResponse(BaseModel):
    id: UUID
    donation_id: UUID
    donor_name: str
    donor_email: str
    donor_phone: str
    amount: float
    message: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
