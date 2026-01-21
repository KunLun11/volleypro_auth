from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditBase


if TYPE_CHECKING:
    from app.db.models.code import VerificationCode


class User(AuditBase):
    __tablename__ = "user_account"

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
        doc="Email",
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Имя пользователя",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Хэш пароля",
    )
    is_active: Mapped[bool] = mapped_column(default=False, doc="Активный")
    is_superuser: Mapped[bool] = mapped_column(default=False, doc="Администратор")
    is_verified: Mapped[bool] = mapped_column(default=False, doc="Верифицирован")

    verification_codes: Mapped[list["VerificationCode"]] = relationship(
        "VerificationCode",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        doc="Коды верификации пользователя",
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
