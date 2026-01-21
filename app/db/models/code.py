from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditBase


if TYPE_CHECKING:
    from app.db.models.user import User


class VerificationCode(AuditBase):
    __tablename__ = "verification_code"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID пользователя",
    )
    code: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
        doc="Код подтверждения",
    )
    is_used: Mapped[bool] = mapped_column(default=False, doc="Был ли использован")
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        doc="Время истечения",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="verification_codes",
        lazy="joined",
        doc="Пользователь",
    )

    def __repr__(self):
        return f"<VerificationCode(id={self.id}, user_id={self.user_id})>"
