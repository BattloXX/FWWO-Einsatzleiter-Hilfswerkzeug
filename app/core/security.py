import hashlib
import secrets
from typing import Optional

import bcrypt
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.config import settings

_signer = URLSafeTimedSerializer(settings.SECRET_KEY, salt="session")
_qr_signer = URLSafeTimedSerializer(settings.SECRET_KEY, salt="qr-token")


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key() -> str:
    return "fwwo_" + secrets.token_urlsafe(32)


def sign_session(user_id: int) -> str:
    return _signer.dumps(user_id)


def unsign_session(token: str) -> Optional[int]:
    try:
        return _signer.loads(token, max_age=settings.SESSION_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None


def sign_qr_token(incident_id: int, user_id: int) -> str:
    return _qr_signer.dumps({"incident_id": incident_id, "user_id": user_id})


def unsign_qr_token(token: str) -> Optional[dict]:
    try:
        return _qr_signer.loads(token)
    except (BadSignature, SignatureExpired):
        return None
