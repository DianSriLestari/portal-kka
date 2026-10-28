from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from typing import Optional
from app.config import COOKIE_NAME
from app.auth import verify_session_token
from app.database import db_session

def get_current_user(request: Request) -> Optional[dict]:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    token_data = verify_session_token(token)
    if not token_data:
        return None
    
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role, class_name FROM users WHERE id = ?", (token_data["user_id"],))
        user = cursor.fetchone()
        if user:
            return dict(user)
    return None

def require_login(request: Request) -> dict:
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    return user

def require_guru(request: Request) -> dict:
    user = require_login(request)
    if user["role"] != "guru":
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/siswa"}
        )
    return user

def require_siswa(request: Request) -> dict:
    user = require_login(request)
    if user["role"] != "siswa":
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/guru"}
        )
    return user
