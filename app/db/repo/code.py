from typing import Optional

from datetime import datetime, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.code import VerificationCode


class VerificationCodeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, verification_code: VerificationCode) -> VerificationCode:
        self.db.add(verification_code)
        await self.db.commit()
        await self.db.refresh(verification_code)
        return verification_code

    async def get_by_id(self, code_id: int) -> Optional[VerificationCode]:
        stmt = select(VerificationCode).where(VerificationCode.id == code_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_code(
        self, user_id: int, code: str
    ) -> Optional[VerificationCode]:
        stmt = select(VerificationCode).where(
            and_(VerificationCode.user_id == user_id, VerificationCode.code == code)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, verification_code: VerificationCode) -> VerificationCode:
        await self.db.commit()
        await self.db.refresh(verification_code)
        return verification_code

    async def delete_expired(self) -> int:
        stmt = select(VerificationCode).where(
            VerificationCode.expires_at <= datetime.now(timezone.utc)
        )
        result = await self.db.execute(stmt)
        expired_codes = result.scalars().all()
        count = len(expired_codes)
        for code in expired_codes:
            await self.db.delete(code)
        await self.db.commit()
        return count
