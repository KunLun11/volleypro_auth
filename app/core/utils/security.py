import logging

from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from app.core.config import settings


logger = logging.getLogger(__name__)


pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    default="argon2",
    deprecated="auto",
    argon2__time_cost=settings.security_argon2_time_cost,
    argon2__memory_cost=settings.security_argon2_memory_cost,
    argon2__parallelism=settings.security_argon2_parallelism,
    bcrypt__rounds=settings.security_bcrypt_rounds,
)


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty")
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise ValueError("Could not hash password")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        logger.warning(f"Unknown hash format: {hashed_password[:20]}...")
        return False
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False
