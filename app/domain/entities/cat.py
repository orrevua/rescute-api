from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.value_objects import Sex


@dataclass
class Cat:
    protector_id: UUID
    name: str
    age_months: int
    sex: Sex
    city: str
    state: str
    sociability: int  # 1-5
    energy: int  # 1-5
    playfulness: int  # 1-5
    id: UUID | None = None
    fiv_status: bool = False
    felv_status: bool = False
    castrated: bool = False
    vaccinated: bool = False
    dewormed: bool = False
    health_needs: str | None = None
    personality: str | None = None
    backstory: str | None = None
    photos: list[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def ready_for_adoption(self) -> bool:
        return self.vaccinated and self.dewormed and self.castrated
