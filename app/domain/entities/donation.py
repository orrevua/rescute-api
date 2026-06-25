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
    is_active: bool = True
    created_at: datetime | None = None
