#==========================#
#     CONFIG/SECURITY.PY   #
#==========================#
from datetime import datetime, timedelta, timezone
import hashlib
import hmac

from jose import jwt
from passlib.context import CryptContext
from app.config.settings import settings
from app.config.logging import get_logger


logger = get_logger(__name__)


hash_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """Hash a plain-text password for secure database storage."""
    return hash_context.hash(password)



def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return whether a plain-text password matches a stored hash."""
    return hash_context.verify(plain_password, hashed_password)


def hash_otp(otp_code : str) -> str:
    """Hash an OTP code with HMAC-SHA256 using the application secret."""
    digest = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        otp_code.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"otp_sha256${digest}"


def hash_auth_secret(secret: str) -> str:
    """Hash a one-time authentication secret for storage."""
    digest = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        secret.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"auth_sha256${digest}"



def verify_otp(otp_code : str, hashed_otp : str):
    """Return whether an OTP code matches the stored OTP hash."""
    if hashed_otp.startswith("otp_sha256$"):
        return hmac.compare_digest(hash_otp(otp_code), hashed_otp)
    return hash_context.verify(otp_code , hashed_otp)


def verify_auth_secret(secret: str, hashed_secret: str) -> bool:
    """Return whether a one-time authentication secret matches the stored hash."""
    if hashed_secret.startswith("auth_sha256$"):
        return hmac.compare_digest(hash_auth_secret(secret), hashed_secret)
    if hashed_secret.startswith("otp_sha256$"):
        return hmac.compare_digest(hash_otp(secret), hashed_secret)
    return hash_context.verify(secret, hashed_secret)



def create_access_token(
        data: dict,  # User information (claims) to be stored inside the JWT
        expires_delta: timedelta | None = None  # Optional custom token lifetime
) -> str:
    """Create and sign a JWT access token with an expiration claim."""

    # Create a copy to avoid modifying the original payload dictionary
    to_encode = data.copy()

    # Calculate when the token should expire.
    # Use the custom expiry if provided, otherwise fall back
    # to the default value configured in settings.
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Add the standard JWT expiration claim ("exp")
    # to the payload before encoding.
    to_encode.update({"exp": expire})

    # Encode and cryptographically sign the payload using
    # the application's secret key and configured algorithm.
    # Returns the final JWT token string.
    return jwt.encode(
        claims=to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


