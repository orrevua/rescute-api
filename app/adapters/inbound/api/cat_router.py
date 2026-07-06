import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.adapters.inbound.api.middleware.auth import get_protector
from app.adapters.inbound.api.schemas.cat import CatCreate, CatListResponse, CatResponse, CatUpdate
from app.application.cat_service import CatService
from app.dependencies import get_cat_service
from app.domain.entities.user import User
from app.domain.value_objects import Sex

log = logging.getLogger(__name__)

router = APIRouter(prefix="/cats", tags=["cats"])


def _response(cat) -> CatResponse:
    return CatResponse.model_validate(cat)


@router.get("", response_model=CatListResponse)
async def list_cats(
    name: str | None = None,
    city: str | None = None,
    state: str | None = Query(default=None, min_length=2, max_length=2),
    sex: Sex | None = None,
    age_min: int | None = Query(default=None, ge=0),
    age_max: int | None = Query(default=None, ge=0),
    service: CatService = Depends(get_cat_service),
) -> CatListResponse:
    cats = await service.list_cats({
        "name": name, "city": city, "state": state, "sex": sex,
        "age_min": age_min, "age_max": age_max,
    })
    return CatListResponse(items=[_response(cat) for cat in cats], total=len(cats))


@router.get("/mine", response_model=list[CatResponse])
async def get_my_cats(
    user: User = Depends(get_protector),
    service: CatService = Depends(get_cat_service),
) -> list[CatResponse]:
    return [_response(cat) for cat in await service.get_my_cats(user.id)]


@router.get("/{cat_id}", response_model=CatResponse)
async def get_cat(cat_id: UUID, service: CatService = Depends(get_cat_service)) -> CatResponse:
    try:
        return _response(await service.get_cat(cat_id))
    except ValueError as error:
        log.warning("Cat lookup failed for %s: %s", cat_id, error)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat not found") from error


@router.post("", response_model=CatResponse, status_code=status.HTTP_201_CREATED)
async def create_cat(
    body: CatCreate,
    user: User = Depends(get_protector),
    service: CatService = Depends(get_cat_service),
) -> CatResponse:
    return _response(await service.create_cat(user.id, body.model_dump()))


@router.patch("/{cat_id}", response_model=CatResponse)
async def update_cat(
    cat_id: UUID,
    body: CatUpdate,
    user: User = Depends(get_protector),
    service: CatService = Depends(get_cat_service),
) -> CatResponse:
    try:
        return _response(await service.update_cat(user.id, cat_id, body.model_dump(exclude_unset=True)))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cat(
    cat_id: UUID,
    user: User = Depends(get_protector),
    service: CatService = Depends(get_cat_service),
) -> None:
    try:
        await service.delete_cat(user.id, cat_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
