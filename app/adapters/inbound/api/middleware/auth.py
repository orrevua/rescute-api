from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from app.config import settings
from app.dependencies import get_user_repository
from app.domain.entities.user import User
from app.domain.ports.repositories import UserRepository
from app.domain.value_objects import UserRole

_ALGORITHM = "HS256"

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    repository: UserRepository = Depends(get_user_repository),
) -> User:
    try:
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=[_ALGORITHM]
        )
        user_id = UUID(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = await repository.find_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


def require_role(role: UserRole):
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return role_checker


get_protector = require_role(UserRole.protector)
get_foster = require_role(UserRole.foster)
