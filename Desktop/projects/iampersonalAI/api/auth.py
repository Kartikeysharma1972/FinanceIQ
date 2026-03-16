"""JWT-based device authentication."""

from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "claw-assistant-secret-change-in-prod"
ALGORITHM = "HS256"


def create_token(device_id: str, expires_hours: int = 720) -> str:
    """Create a JWT token for a device (default 30 days)."""
    payload = {
        "sub": device_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=expires_hours),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[str]:
    """Verify token and return device_id."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
