from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.value_objects import NegotiationStatus


@dataclass
class Partner:
    name: str
    address: str
    cep: str
    city: str
    state: str
    id: UUID | None = None
    description: str | None = None
    lat: float | None = None
    lng: float | None = None
    coupon_code: str | None = None
    discount_pct: int | None = None
    is_active: bool = True
    owner_id: UUID | None = None


@dataclass
class PartnerNegotiation:
    partner_id: UUID
    host_id: UUID
    proposed_amount: float
    contact_email: str
    contact_phone: str
    id: UUID | None = None
    proposed_message: str | None = None
    status: NegotiationStatus = NegotiationStatus.pending
    counter_amount: float | None = None
    counter_message: str | None = None
    created_at: datetime | None = None
