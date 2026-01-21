from fastapi import APIRouter, Depends, HTTPException, status

from app.deps.auth import get_auth_service, get_current_active_user
from app.deps.user import get_user_service
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService
from app.services.user import UserService
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResendCodeRequest,
    Token,
    VerifyEmailRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.authenticate_user(
        email=login_data.email,
        password=login_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    tokens = auth_service.create_tokens(user.id, user.email, user.is_active)
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user_id=user.id,
        email=user.email,
        is_active=user.is_active,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    register_data: RegisterRequest,
    user_service: UserService = Depends(get_user_service),
):
    try:
        user_create = UserCreate(
            email=register_data.email,
            username=register_data.username,
            password=register_data.password,
        )
        existing_user = await user_service.get_user_by_email(register_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with email already exists",
            )
        user = await user_service.create_user(user_create)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error for registration: {str(e)}",
        )


@router.post("/verify-email", response_model=dict)
async def verify_email(
    verify_data: VerifyEmailRequest,
    user_service: UserService = Depends(get_user_service),
):
    verify = await user_service.verify_email(
        email=verify_data.email,
        code=verify_data.code,
    )
    if not verify:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verifcation code or email",
        )

    return {
        "message": "Email успешно подтвержден. Аккаунт активирован.",
        "email": verify_data.email,
    }


@router.post("/resend-code", response_model=dict)
async def resend_verification_code(
    resend_data: ResendCodeRequest,
    user_service: UserService = Depends(get_user_service),
):
    resend = await user_service.resend_verification_code(resend_data.email)
    if not resend:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Couldn't send the code.",
        )
    return {
        "message": "Код подтверждения отправлен на email",
        "email": resend_data.email,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    tokens = await auth_service.refresh_tokens(refresh_request.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return Token(**tokens)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_active_user),
):
    return current_user


# @router.post("/logout")
# async def logout():
#     return {"message": "Successfully logged out"}
