import os
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.adapters.inbound.api.middleware.auth import get_current_user
from app.domain.entities.user import User

router = APIRouter(prefix="/uploads", tags=["uploads"])

_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
_UPLOADS_DIR = "uploads"


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    _user: User = Depends(get_current_user),
) -> dict[str, str]:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are accepted",
        )

    contents = await file.read()

    if len(contents) > _MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 5MB limit",
        )

    ext = os.path.splitext(file.filename or "")[1]
    unique_name = f"{uuid4()}{ext}"
    filepath = os.path.join(_UPLOADS_DIR, unique_name)

    with open(filepath, "wb") as f:
        f.write(contents)

    return {"url": f"/uploads/{unique_name}"}
