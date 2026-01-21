from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend

from fastapi import Request
from sqlalchemy import select

from app.core.utils.security import verify_password
from app.db.models.code import VerificationCode
from app.db.models.user import User

from app.core.session import AsyncSessionLocal, engine
from app.core.config import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        if not email or not password:
            return False

        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user and user.is_superuser:
                if verify_password(password, user.password_hash):
                    request.session.update({"admin": True})
                    return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("admin", False))


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.email,
        User.username,
        User.is_active,
        User.created_at,
    ]
    column_searchable_list = [User.email, User.username]
    column_sortable_list = [User.id, User.email, User.created_at]
    form_excluded_columns = [User.password_hash]


class VerificationCodeAdmin(ModelView, model=VerificationCode):
    column_list = [
        VerificationCode.id,
        VerificationCode.user_id,
        VerificationCode.code,
        VerificationCode.is_used,
        VerificationCode.created_at,
        VerificationCode.expires_at,
    ]
    column_sortable_list = [VerificationCode.id, VerificationCode.created_at]


def setup_admin(app):
    authentication_backend = AdminAuth(secret_key=settings.secret_key)

    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="VolleyPRO Admin",
        base_url="/admin",
    )

    admin.add_view(UserAdmin)
    admin.add_view(VerificationCodeAdmin)

    return admin
