from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from pydantic import BaseModel
from typing import List, Optional
import csv
import io
import json
from app.database import db_session, log_activity
from app.auth import hash_password, create_session_token, verify_password
from app.dependencies import get_current_user, require_guru, require_siswa

router = APIRouter(prefix="/api", tags=["REST API"])

# Pydantic Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class SiswaCreateRequest(BaseModel):
    username: str
    password: str
    full_name: str
    class_name: str = "X-1"

class SimulationStateRequest(BaseModel):
    unit_id: int = 1
    activity_key: str
    score: int = 0
    state_data: dict

# 1. API: Login & Token
@router.post("/auth/login", summary="Login REST API")
def api_login(payload: LoginRequest):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, salt, full_name, role, class_name FROM users WHERE username = ?", (payload.username.strip(),))
        user = cursor.fetchone()
        if not user or not verify_password(payload.password, user["password_hash"], user["salt"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kredensial tidak valid")
        
        token = create_session_token(user["id"], user["username"], user["role"])
        log_activity(user["id"], "API_LOGIN", f"Login via REST API: {user['full_name']}", conn=conn)
        
        return {
            "status": "success",
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"],
                "class_name": user["class_name"]
            }
        }

# 2. API: Get Student List (Khusus Guru)
@router.get("/siswa", summary="Daftar Siswa Lengkap")
def api_get_siswa(user: dict = Depends(require_guru)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, full_name, class_name, created_at,
                   (SELECT COUNT(*) FROM activity_logs WHERE user_id = users.id) as total_interactions,
                   (SELECT MAX(created_at) FROM activity_logs WHERE user_id = users.id) as last_seen
            FROM users
            WHERE role = 'siswa'
            ORDER BY full_name ASC
        """)
        return {"status": "success", "data": [dict(row) for row in cursor.fetchall()]}

# 3. API: Create Student
@router.post("/siswa", summary="Tambah Akun Siswa Baru")
def api_create_siswa(payload: SiswaCreateRequest, user: dict = Depends(require_guru)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (payload.username.strip(),))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username sudah digunakan")
        
        pw_hash, salt = hash_password(payload.password)
        cursor.execute("""
            INSERT INTO users (username, password_hash, salt, full_name, role, class_name)
            VALUES (?, ?, ?, ?, 'siswa', ?)
        """, (payload.username.strip(), pw_hash, salt, payload.full_name.strip(), payload.class_name))
        new_id = cursor.lastrowid
        log_activity(user["id"], "API_TAMBAH_SISWA", f"Menambah siswa baru #{new_id} via API", conn=conn)
        
        return {"status": "success", "message": "Akun siswa berhasil dibuat", "siswa_id": new_id}

# 4. API: Bulk Import Siswa from CSV
@router.post("/siswa/bulk-import", summary="Import Massal Akun Siswa dari CSV")
async def api_bulk_import_siswa(file: UploadFile = File(...), user: dict = Depends(require_guru)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Harap unggah file dengan format .csv")
    
    contents = await file.read()
    decoded = contents.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))
    
    added_count = 0
    skipped_count = 0
    
    with db_session() as conn:
        cursor = conn.cursor()
        for row in reader:
            username = row.get("username", "").strip()
            password = row.get("password", "siswa123").strip()
            full_name = row.get("full_name", "").strip()
            class_name = row.get("class_name", "X-1").strip()
            
            if not username or not full_name:
                continue
                
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                skipped_count += 1
                continue
                
            pw_hash, salt = hash_password(password)
            cursor.execute("""
                INSERT INTO users (username, password_hash, salt, full_name, role, class_name)
                VALUES (?, ?, ?, ?, 'siswa', ?)
            """, (username, pw_hash, salt, full_name, class_name))
            added_count += 1
            
        log_activity(user["id"], "API_BULK_IMPORT", f"Import massal: {added_count} ditambahkan, {skipped_count} dilewati", conn=conn)

    return {
        "status": "success",
        "message": f"Import massal berhasil. {added_count} siswa ditambahkan, {skipped_count} akun dilewati (duplikat)."
    }

# 5. API: Delete Student
@router.delete("/siswa/{siswa_id}", summary="Hapus Akun Siswa")
def api_delete_siswa(siswa_id: int, user: dict = Depends(require_guru)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name FROM users WHERE id = ? AND role = 'siswa'", (siswa_id,))
        target = cursor.fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
            
        cursor.execute("DELETE FROM users WHERE id = ?", (siswa_id,))
        log_activity(user["id"], "API_HAPUS_SISWA", f"Menghapus siswa {target['full_name']} via API", conn=conn)
        return {"status": "success", "message": f"Siswa {target['full_name']} telah dihapus"}

# 6. API: Get Activity Logs (Khusus Guru)
@router.get("/logs", summary="Ambil Data Audit Log Aktivitas")
def api_get_logs(limit: int = 50, user: dict = Depends(require_guru)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.id, l.action, l.details, l.created_at, l.ip_address, u.full_name, u.role
            FROM activity_logs l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.created_at DESC
            LIMIT ?
        """, (limit,))
        return {"status": "success", "data": [dict(row) for row in cursor.fetchall()]}

# 7. API: Save Interactive Simulation State
@router.post("/simulasi/state", summary="Simpan Status/Hasil Lab Simulasi Siswa")
def api_save_simulation_state(payload: SimulationStateRequest, user: dict = Depends(require_siswa)):
    with db_session() as conn:
        cursor = conn.cursor()
        state_str = json.dumps(payload.state_data)
        cursor.execute("""
            INSERT INTO interactive_progress (user_id, unit_id, activity_key, score, state_data, completed, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, unit_id, activity_key) DO UPDATE SET
                score = excluded.score,
                state_data = excluded.state_data,
                completed = 1,
                updated_at = CURRENT_TIMESTAMP
        """, (user["id"], payload.unit_id, payload.activity_key, payload.score, state_str))
        
        log_activity(user["id"], "SIMPAN_SIMULASI", f"Menyimpan capaian lab '{payload.activity_key}' skor: {payload.score}", conn=conn)
        return {"status": "success", "message": "Progres simulasi berhasil disimpan ke database"}

# 8. API: Get Units & Lessons List
@router.get("/materi", summary="Daftar Modul & Pertemuan Pembelajaran")
def api_get_materi():
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM units ORDER BY unit_number ASC")
        units = [dict(u) for u in cursor.fetchall()]
        
        cursor.execute("SELECT id, unit_id, meeting_number, title, tp_focus, duration, interactive_type FROM lessons ORDER BY meeting_number ASC")
        lessons = [dict(l) for l in cursor.fetchall()]
        
        return {
            "status": "success",
            "units": units,
            "lessons": lessons
        }
