from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    protector = "protector"
    foster = "foster"


class ApplicationStatus(str, Enum):
    pending = "pending"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"


class DonationType(str, Enum):
    financial = "financial"
    item = "item"


class Sex(str, Enum):
    male = "male"
    female = "female"


@dataclass(frozen=True)
class Location:
    city: str
    state: str
    cep: str | None = None
    lat: float | None = None
    lng: float | None = None


@dataclass(frozen=True)
class HealthProfile:
    fiv: bool
    felv: bool
    castrated: bool
    vaccinated: bool
    dewormed: bool
    health_needs: str | None = None


@dataclass(frozen=True)
class PersonalityTraits:
    sociability: int  # 1-5
    energy: int  # 1-5
    playfulness: int  # 1-5

    def __post_init__(self) -> None:
        for field in ("sociability", "energy", "playfulness"):
            value = getattr(self, field)
            if not (1 <= value <= 5):
                raise ValueError(f"{field} must be between 1 and 5, got {value}")
