import hashlib
import hmac
import secrets
import time
from typing import Optional, Tuple
from app.config import SECRET_KEY

def generate_salt() -> str:
    return secrets.token_hex(16)

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    if salt is None:
        salt = generate_salt()
    # PBKDF2 HMAC SHA-256 with 100,000 iterations
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return key.hex(), salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    check_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(check_hash, hashed)

def create_session_token(user_id: int, username: str, role: str) -> str:
    timestamp = str(int(time.time()))
    payload = f"{user_id}:{username}:{role}:{timestamp}"
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"

def verify_session_token(token: str, max_age_hours: int = 24) -> Optional[dict]:
    if not token or ":" not in token:
        return None
    try:
        parts = token.split(":")
        if len(parts) != 5:
            return None
        user_id, username, role, timestamp, signature = parts
        payload = f"{user_id}:{username}:{role}:{timestamp}"
        expected_sig = hmac.new(
            SECRET_KEY.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_sig, signature):
            return None
            
        token_time = int(timestamp)
        current_time = int(time.time())
        if current_time - token_time > max_age_hours * 3600:
            return None  # expired
            
        return {
            "user_id": int(user_id),
            "username": username,
            "role": role,
            "created_at": token_time
        }
    except Exception:
        return None
