import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

security_scheme = HTTPBearer(auto_error=False)

CARD_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?91[-\s]?)?[6-9]\d{9}\b")
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w]{2,}\b")


def scrub_pii(text: str) -> str:
    text = CARD_PATTERN.sub("[REDACTED_CARD]", text)
    text = PHONE_PATTERN.sub("[REDACTED_PHONE]", text)
    text = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
    return text


def create_access_token(sub: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    payload = {
        "sub": sub,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.jwt_expiry_minutes)),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return decode_token(credentials.credentials)


def require_role(*allowed_roles: str):
    async def role_checker(payload: dict = Depends(get_current_user)):
        if payload.get("role") not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return payload
    return role_checker
