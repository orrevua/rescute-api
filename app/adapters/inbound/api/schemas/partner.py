from uuid import UUID

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)
