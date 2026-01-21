import jwt

from typing import Any, Optional

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.utils.jwt import create_access_token, create_refresh_token, verify_token
from app.core.utils.security import verify_password
from app.services.user import UserService


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.secret = settings.secret_key
        self.algorithm = settings.algorithm

    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        user = await self.user_service.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user

    def create_tokens(
        self,
        user_id: int,
        email: str,
        is_active: bool,
    ) -> dict[str, Any]:
        access_token = create_access_token(
            data={
                "sub": str(user_id),
                "email": email,
                "is_active": is_active,
            }
        )
        refresh_token = create_refresh_token(
            data={
                "sub": str(user_id),
                "email": email,
                "is_active": is_active,
            }
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user_id,
            "email": email,
            "is_active": is_active,
        }

    async def refresh_tokens(self, refresh_token: str) -> Optional[dict[str, Any]]:
        try:
            payload = verify_token(refresh_token)

            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            user_id = int(payload.get("sub"))
            email = payload.get("email")

            user = await self.user_service.get_user(user_id)
            if not user:
                return None
            return self.create_tokens(user_id, email)

        except (jwt.PyJWTError, ValueError, KeyError):
            return None
