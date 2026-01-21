from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends

from app.db.repo.code import VerificationCodeRepository
from app.db.repo.user import UserRepository
from app.core.session import get_db
from app.services.user import UserService


async def get_user_repo(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[UserRepository, None]:
    yield UserRepository(db)


async def get_verification_code_repo(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[VerificationCodeRepository, None]:
    yield VerificationCodeRepository(db)


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
    code_repo: VerificationCodeRepository = Depends(get_verification_code_repo),
) -> AsyncGenerator[UserService, None]:
    yield UserService(user_repo, code_repo)
