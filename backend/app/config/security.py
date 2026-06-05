#==========================#
#     CONFIG/SECURITY.PY   #
#==========================#
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from backend.app.config.settings import settings
from backend.app.config.logging import get_logger


logger = get_logger(__name__)


hash_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return hash_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_context.verify(plain_password, hashed_password)



def hash_otp(otp_code : str) -> str:
    return hash_context.hash(otp_code)


def verify_otp(otp_code : str, hashed_otp : str):
    return hash_context.verify(otp_code , hashed_otp)


def create_access_token(
        data: dict,
        expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        claims=to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

