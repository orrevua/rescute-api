import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.adapters.inbound.api.middleware.auth import get_current_user
from app.adapters.inbound.api.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.application.auth_service import AuthService
from app.dependencies import get_auth_service
from app.domain.entities.user import User
from app.rate_limit import limiter

log = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        user, access, refresh = await service.register(
            email=body.email,
            password=body.password,
            role=body.role,
            profile_data=body.model_dump(exclude={"email", "password", "role"}),
        )
    except ValueError as e:
        log.warning("Registration rejected: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return AuthResponse(
        user=UserResponse(id=user.id, email=user.email, role=user.role),
        access_token=access,
        refresh_token=refresh,
    )


@router.post("/login", response_model=AuthResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        user, access, refresh = await service.login(body.email, body.password)
    except ValueError as e:
        log.warning("Login rejected: %s", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return AuthResponse(
        user=UserResponse(id=user.id, email=user.email, role=user.role),
        access_token=access,
        refresh_token=refresh,
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    body: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        user = await service.verify_refresh_token(body.refresh_token)
        access = service._create_access_token(user.id, user.role.value)
        new_refresh = service._create_refresh_token(user.id, user.token_version)
    except ValueError as e:
        log.warning("Refresh rejected: %s", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> None:
    await service.logout(user.id)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, role=user.role)
