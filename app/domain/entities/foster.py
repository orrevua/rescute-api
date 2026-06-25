from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.value_objects import ApplicationStatus


@dataclass
class FosterApplication:
    user_id: UUID
    existing_pets: str
    compatibility: str
    prior_experience: str
    city: str
    cost_aware: bool
    id: UUID | None = None
    status: ApplicationStatus = ApplicationStatus.pending
    created_at: datetime | None = None
