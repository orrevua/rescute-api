from dataclasses import dataclass
from uuid import UUID


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
