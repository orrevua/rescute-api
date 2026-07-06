import os
from uuid import uuid4

import filetype
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.adapters.inbound.api.middleware.auth import get_current_user
from app.domain.entities.user import User

router = APIRouter(prefix="/uploads", tags=["uploads"])

_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
_UPLOADS_DIR = "uploads"
# Real content type (sniffed by magic bytes) -> safe stored extension.
_ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    _user: User = Depends(get_current_user),
) -> dict[str, str]:
    contents = await file.read()

    if len(contents) > _MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 5MB limit",
        )

    kind = filetype.guess(contents)
    if kind is None or kind.mime not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG or WebP images are accepted",
        )

    unique_name = f"{uuid4()}{_ALLOWED_TYPES[kind.mime]}"
    filepath = os.path.join(_UPLOADS_DIR, unique_name)

    with open(filepath, "wb") as f:
        f.write(contents)

    # Files are served with Content-Disposition: attachment (see security middleware).
    return {"url": f"/uploads/{unique_name}"}
