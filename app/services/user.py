from datetime import datetime, timedelta, timezone
import logging
from typing import Optional

from app.core.utils.security import hash_password
from app.db.models.code import VerificationCode
from app.db.models.user import User
from app.db.repo.code import VerificationCodeRepository
from app.db.repo.user import UserRepository
from app.schemas.user import UserCreate
from app.services.email import EmailService

from app.core.utils.email_code import generate_verification_code


logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        code_repository: VerificationCodeRepository,
    ):
        self.user_repo = user_repository
        self.code_repo = code_repository
        self.email_service = EmailService()

    async def get_user(self, user_id: int) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.user_repo.get_by_email(email)

    async def create_user(self, user_create: UserCreate) -> User:
        existing_user = await self.get_user_by_email(user_create.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        hashed_password = hash_password(user_create.password)
        db_user = User(
            email=user_create.email,
            password_hash=hashed_password,
            username=user_create.username,
            is_active=False,
            is_verified=False,
            is_superuser=False,
        )
        user = await self.user_repo.create(db_user)
        code = generate_verification_code()
        verification_code = VerificationCode(
            user_id=user.id,
            code=code,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        await self.code_repo.create(verification_code)
        success = await self.email_service.send_verification_email(user.email, code)
        if success:
            logger.info("Email отправлен успешно")
        else:
            logger.warning("Не удалось отправить email, но пользователь создан")
        return user

    async def verify_email(self, email: str, code: str) -> bool:
        user = await self.get_user_by_email(email)
        if not user:
            return False

        verification_code = await self.code_repo.get_by_user_and_code(user.id, code)
        if not verification_code:
            return False

        now = datetime.now(timezone.utc)
        if verification_code.is_used or verification_code.expires_at <= now:
            return False

        verification_code.is_used = True
        await self.code_repo.update(verification_code)

        user.is_active = True
        user.is_verified = True
        await self.user_repo.update(user)

        # await self.email_service.send_welcome_email(user.email)
        return True

    async def resend_verification_code(self, email) -> bool:
        user = await self.get_user_by_email(email)
        if not user or user.is_verified:
            return False
        actice_codes = await self.code_repo.get_active_by_user(user.id)
        if actice_codes:
            code = actice_codes[0].code
            await self.email_service.send_verification_email(email, code)
        else:
            code = generate_verification_code()
            verification_code = VerificationCode(
                user_id=user.id,
                code=code,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
            )
            await self.code_repo.create(verification_code)
            await self.email_service.send_verification_email(user.email, code)
        return True

    async def delete_user(self, user_id: int) -> bool:
        return await self.user_repo.delete(user_id)
