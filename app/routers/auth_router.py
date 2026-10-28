from fastapi import APIRouter, Request, Form, Response, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.config import TEMPLATES_DIR, COOKIE_NAME
from app.database import db_session, log_activity
from app.auth import verify_password, create_session_token
from app.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    if user["role"] == "guru":
        return RedirectResponse(url="/guru", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/siswa", status_code=status.HTTP_302_FOUND)

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, msg: str = None, err: str = None):
    user = get_current_user(request)
    if user:
        if user["role"] == "guru":
            return RedirectResponse(url="/guru", status_code=status.HTTP_302_FOUND)
        return RedirectResponse(url="/siswa", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="auth/login.html", context={"user": None, "error": err, "msg": msg})

@router.post("/login", response_class=HTMLResponse)
def login_post(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    username = username.strip()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, salt, full_name, role, class_name, must_change_password FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        
        if not user_row:
            return templates.TemplateResponse(request=request, name="auth/login.html", context={
                "user": None,
                "error": "Nama pengguna tidak ditemukan. Periksa kembali username Anda.",
                "msg": None
            }, status_code=400)
            
        is_valid = verify_password(password, user_row["password_hash"], user_row["salt"])
        if not is_valid:
            return templates.TemplateResponse(request=request, name="auth/login.html", context={
                "user": None,
                "error": "Kata sandi salah. Silakan coba lagi atau ajukan lupa password.",
                "msg": None
            }, status_code=400)

        # Create session token
        token = create_session_token(user_row["id"], user_row["username"], user_row["role"])
        
        # Log activity
        client_ip = request.client.host if request.client else "127.0.0.1"
        log_activity(user_row["id"], "LOGIN", f"Pengguna {user_row['full_name']} ({user_row['role']}) berhasil login", client_ip, conn=conn)

        redirect_url = "/guru" if user_row["role"] == "guru" else "/siswa"
        if user_row["role"] == "siswa" and user_row["must_change_password"] == 1:
            redirect_url = "/siswa/ganti-password?notice=temp_pw"

        resp = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
        resp.set_cookie(
            key=COOKIE_NAME,
            value=token,
            max_age=86400,
            httponly=True,
            samesite="lax"
        )
        return resp

# ==========================================
# LUPA PASSWORD / RESET REQUEST
# ==========================================
@router.get("/lupa-password", response_class=HTMLResponse)
def lupa_password_page(request: Request, msg: str = None, err: str = None):
    return templates.TemplateResponse(request=request, name="auth/lupa_password.html", context={
        "user": None,
        "msg": msg,
        "err": err,
        "check_result": None
    })

@router.post("/lupa-password")
def submit_lupa_password(request: Request, username: str = Form(...), reason: str = Form("Lupa kata sandi")):
    username = username.strip()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, class_name, role FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        
        if not user_row:
            return templates.TemplateResponse(request=request, name="auth/lupa_password.html", context={
                "user": None,
                "err": f"Username '@{username}' tidak terdaftar di sistem. Periksa kembali NISN/username Anda.",
                "msg": None,
                "check_result": None
            }, status_code=400)
            
        # Cek apakah sudah ada request pending
        cursor.execute("SELECT id FROM password_reset_requests WHERE user_id = ? AND status = 'pending'", (user_row["id"],))
        if cursor.fetchone():
            return templates.TemplateResponse(request=request, name="auth/lupa_password.html", context={
                "user": None,
                "msg": f"Permintaan reset kata sandi untuk '@{username}' sudah pernah diajukan dan sedang menunggu persetujuan Guru.",
                "err": None,
                "check_result": None
            })
            
        cursor.execute("""
            INSERT INTO password_reset_requests (user_id, username, full_name, class_name, reason, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (user_row["id"], user_row["username"], user_row["full_name"], user_row["class_name"], reason))
        
        log_activity(user_row["id"], "MINTA_RESET_PW", f"Siswa {user_row['full_name']} mengajukan permohonan reset password", conn=conn)

    return templates.TemplateResponse(request=request, name="auth/lupa_password.html", context={
        "user": None,
        "msg": f"Permintaan reset kata sandi untuk '@{username}' ({user_row['full_name']}) berhasil dikirim ke Guru KKA! Silakan beri tahu Guru Anda untuk menyetujui reset dan melihat kata sandi sementara.",
        "err": None,
        "check_result": None
    })

@router.get("/lupa-password/cek", response_class=HTMLResponse)
def cek_status_reset(request: Request, username: str = Query(...)):
    username = username.strip()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM password_reset_requests 
            WHERE username = ? 
            ORDER BY created_at DESC LIMIT 1
        """, (username,))
        row = cursor.fetchone()
        
        check_result = dict(row) if row else {"username": username, "status": "none"}

    return templates.TemplateResponse(request=request, name="auth/lupa_password.html", context={
        "user": None,
        "msg": None,
        "err": None,
        "check_result": check_result
    })

@router.get("/logout")
def logout(request: Request):
    user = get_current_user(request)
    if user:
        client_ip = request.client.host if request.client else "127.0.0.1"
        log_activity(user["id"], "LOGOUT", f"Pengguna {user['full_name']} logout", client_ip)
        
    resp = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    resp.delete_cookie(COOKIE_NAME)
    return resp
