from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.value_objects import ApplicationStatus


@dataclass
class AdoptionApplication:
    cat_id: UUID
    applicant_name: str
    applicant_email: str
    applicant_phone: str
    id: UUID | None = None
    message: str | None = None
    accepted_terms: bool = True
    status: ApplicationStatus = ApplicationStatus.pending
    created_at: datetime | None = None
