from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return AuthResponse(
        user=UserResponse(id=user.id, email=user.email, role=user.role),
        access_token=access,
        refresh_token=refresh,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        user, access, refresh = await service.login(body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return AuthResponse(
        user=UserResponse(id=user.id, email=user.email, role=user.role),
        access_token=access,
        refresh_token=refresh,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        user = await service.get_current_user(body.refresh_token)
        access = service._create_access_token(user.id, user.role.value)
        new_refresh = service._create_refresh_token(user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, role=user.role)
