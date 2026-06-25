from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.value_objects import DonationType


@dataclass
class DonationPost:
    protector_id: UUID
    title: str
    description: str
    type: DonationType
    id: UUID | None = None
    target_amount: float | None = None
    current_amount: float = 0.0
    payment_link: str | None = None
    is_active: bool = True
    created_at: datetime | None = None


@dataclass
class DonationIntent:
    donation_id: UUID
    donor_name: str
    donor_email: str
    donor_phone: str
    amount: float
    message: str | None = None
    id: UUID | None = None
    created_at: datetime | None = None
