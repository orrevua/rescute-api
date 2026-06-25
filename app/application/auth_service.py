from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.domain.entities.user import FosterProfile, ProtectorProfile, User
from app.domain.ports.repositories import UserRepository
from app.domain.value_objects import UserRole

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
_ALGORITHM = "HS256"


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def register(
        self, email: str, password: str, role: UserRole, profile_data: dict
    ) -> tuple[User, str, str]:
        if await self._user_repo.find_by_email(email):
            raise ValueError("Email already registered")
        user = User(
            email=email,
            hashed_password=_pwd_ctx.hash(password),
            role=role,
        )
        user = await self._user_repo.save(user)
        if user.id is None:
            raise RuntimeError("A registered user must have an id")
        if role is UserRole.protector:
            org_name = profile_data.get("org_name")
            if not org_name:
                raise ValueError("Organization name is required for protectors")
            await self._user_repo.save_protector_profile(
                ProtectorProfile(
                    user_id=user.id, org_name=org_name,
                    description=profile_data.get("description"), phone=profile_data.get("phone"),
                    city=profile_data.get("city"), state=profile_data.get("state"),
                )
            )
        else:
            required = ("full_name", "phone", "city", "state")
            if any(not profile_data.get(field) for field in required):
                raise ValueError("Full name, phone, city and state are required for foster applicants")
            await self._user_repo.save_foster_profile(
                FosterProfile(
                    user_id=user.id, full_name=profile_data["full_name"], phone=profile_data["phone"],
                    city=profile_data["city"], state=profile_data["state"],
                )
            )
        return user, self._create_access_token(user.id, user.role.value), self._create_refresh_token(user.id)

    async def login(self, email: str, password: str) -> tuple[User, str, str]:
        user = await self._user_repo.find_by_email(email)
        if not user or not _pwd_ctx.verify(password, user.hashed_password):
            raise ValueError("Invalid email or password")
        return user, self._create_access_token(user.id, user.role.value), self._create_refresh_token(user.id)

    async def get_current_user(self, token: str) -> User:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[_ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise ValueError("Invalid token")
        except JWTError:
            raise ValueError("Invalid token")
        user = await self._user_repo.find_by_id(UUID(user_id))
        if not user:
            raise ValueError("User not found")
        return user

    def _create_access_token(self, user_id: UUID, role: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return jwt.encode({"sub": str(user_id), "role": role, "exp": expire}, settings.SECRET_KEY, algorithm=_ALGORITHM)

    def _create_refresh_token(self, user_id: UUID) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return jwt.encode({"sub": str(user_id), "exp": expire}, settings.SECRET_KEY, algorithm=_ALGORITHM)
