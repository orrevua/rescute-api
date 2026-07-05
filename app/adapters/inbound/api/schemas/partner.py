from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.value_objects import NegotiationStatus, UserRole


class PartnerResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    address: str
    cep: str
    city: str
    state: str
    lat: float | None
    lng: float | None
    coupon_code: str | None
    discount_pct: int | None
    is_active: bool
    owner_id: UUID | None

    model_config = ConfigDict(from_attributes=True)


class HostResponse(BaseModel):
    user_id: UUID
    role: UserRole
    display_name: str
    city: str | None = None
    state: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PartnerRegister(BaseModel):
    name: str
    description: str | None = None
    address: str
    cep: str
    city: str
    state: str
    coupon_code: str | None = None
    discount_pct: int | None = None
    host_id: UUID
    proposed_amount: float = Field(gt=0)
    proposed_message: str | None = None
    contact_email: str
    contact_phone: str


class NegotiationResponse(BaseModel):
    id: UUID
    status: NegotiationStatus
    proposed_amount: float
    proposed_message: str | None
    contact_email: str
    contact_phone: str
    counter_amount: float | None
    counter_message: str | None
    created_at: datetime
    partner: PartnerResponse

    model_config = ConfigDict(from_attributes=True)


class NegotiationAction(BaseModel):
    action: Literal["accept", "reject", "counter"]
    counter_amount: float | None = Field(default=None, gt=0)
    counter_message: str | None = None


class PartnerUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    address: str | None = None
    cep: str | None = None
    city: str | None = None
    state: str | None = None
    coupon_code: str | None = None
    discount_pct: int | None = None
