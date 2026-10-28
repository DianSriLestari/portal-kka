from fastapi import APIRouter, Request, Form, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, Response, FileResponse
from fastapi.templating import Jinja2Templates
import csv
import io
import os
import secrets
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from app.config import TEMPLATES_DIR, SLIDES_DIR
from app.database import db_session, log_activity
from app.auth import hash_password
from app.dependencies import require_guru

router = APIRouter(prefix="/guru")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("", response_class=HTMLResponse)
def guru_dashboard(request: Request, user: dict = Depends(require_guru)):
    with db_session() as conn:
        cursor = conn.cursor()
        
        # Stats
        total_siswa = cursor.execute("SELECT COUNT(*) as c FROM users WHERE role = 'siswa'").fetchone()["c"]
        total_materi = cursor.execute("SELECT COUNT(*) as c FROM lessons").fetchone()["c"]
        total_kuis = cursor.execute("SELECT COUNT(*) as c FROM quizzes").fetchone()["c"]
        total_tugas = cursor.execute("SELECT COUNT(*) as c FROM submissions").fetchone()["c"]
        
        # Pending reset requests count
        cursor.execute("SELECT COUNT(*) as c FROM password_reset_requests WHERE status = 'pending'")
        pending_resets = cursor.fetchone()["c"]

        # Pending remedial requests count
        cursor.execute("SELECT COUNT(*) as c FROM quiz_remedial_requests WHERE status = 'pending'")
        pending_remedials = cursor.fetchone()["c"]

        # Pending reset requests list (top 5)
        cursor.execute("""
            SELECT * FROM password_reset_requests 
            WHERE status = 'pending' 
            ORDER BY created_at DESC LIMIT 5
        """)
        pending_reset_list = [dict(r) for r in cursor.fetchall()]

        # Recent logs (15 latest)
        cursor.execute("""
            SELECT l.id, l.action, l.details, l.created_at, l.ip_address, u.full_name, u.role, u.class_name
            FROM activity_logs l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.created_at DESC
            LIMIT 15
        """)
        recent_logs = [dict(row) for row in cursor.fetchall()]

        # Student progress overview
        cursor.execute("""
            SELECT u.id, u.username, u.full_name, u.class_name,
                (SELECT COUNT(*) FROM activity_logs WHERE user_id = u.id AND action LIKE '%MODUL%') as lessons_read,
                (SELECT COUNT(*) FROM quiz_attempts WHERE user_id = u.id) as quizzes_taken,
                (SELECT AVG(score) FROM quiz_attempts WHERE user_id = u.id) as avg_quiz_score,
                (SELECT COUNT(*) FROM submissions WHERE user_id = u.id) as submissions_count
            FROM users u
            WHERE u.role = 'siswa'
            ORDER BY u.full_name ASC
        """)
        student_progress = [dict(row) for row in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="guru/dashboard.html", context={
        "user": user,
        "active_nav": "dashboard",
        "total_siswa": total_siswa,
        "total_materi": total_materi,
        "total_kuis": total_kuis,
        "total_tugas": total_tugas,
        "pending_resets": pending_resets,
        "pending_remedials": pending_remedials,
        "pending_reset_list": pending_reset_list,
        "recent_logs": recent_logs,
        "student_progress": student_progress
    })

# ==========================================
# GURU: KELOLA SISWA & RESET PASSWORD
# ==========================================
@router.get("/siswa", response_class=HTMLResponse)
def kelola_siswa_page(request: Request, user: dict = Depends(require_guru), msg: str = None, err: str = None):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.full_name, u.class_name, u.must_change_password, u.created_at,
                   (SELECT COUNT(*) FROM activity_logs WHERE user_id = u.id) as total_activities,
                   (SELECT MAX(created_at) FROM activity_logs WHERE user_id = u.id) as last_seen
            FROM users u
            WHERE u.role = 'siswa'
            ORDER BY u.created_at DESC
        """)
        siswa_list = [dict(row) for row in cursor.fetchall()]

        # Password reset requests
        cursor.execute("""
            SELECT * FROM password_reset_requests 
            ORDER BY CASE WHEN status = 'pending' THEN 0 ELSE 1 END, created_at DESC
        """)
        reset_requests = [dict(r) for r in cursor.fetchall()]
        pending_resets = sum(1 for r in reset_requests if r["status"] == "pending")

    return templates.TemplateResponse(request=request, name="guru/siswa.html", context={
        "user": user,
        "active_nav": "siswa",
        "siswa_list": siswa_list,
        "reset_requests": reset_requests,
        "pending_resets": pending_resets,
        "msg": msg,
        "err": err
    })

@router.post("/siswa/tambah")
def tambah_siswa(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    class_name: str = Form("X-1"),
    user: dict = Depends(require_guru)
):
    username = username.strip()
    full_name = full_name.strip()
    
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return RedirectResponse(url="/guru/siswa?err=Username+sudah+digunakan", status_code=status.HTTP_302_FOUND)
        
        pw_hash, salt = hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, password_hash, salt, full_name, role, class_name)
            VALUES (?, ?, ?, ?, 'siswa', ?)
        """, (username, pw_hash, salt, full_name, class_name))
        
        log_activity(user["id"], "TAMBAH_SISWA", f"Guru menambahkan siswa baru: {full_name} ({username})", conn=conn)

    return RedirectResponse(url="/guru/siswa?msg=Siswa+berhasil+ditambahkan", status_code=status.HTTP_302_FOUND)

@router.post("/siswa/hapus/{siswa_id}")
def hapus_siswa(siswa_id: int, user: dict = Depends(require_guru)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, username FROM users WHERE id = ? AND role = 'siswa'", (siswa_id,))
        target = cursor.fetchone()
        if target:
            cursor.execute("DELETE FROM users WHERE id = ?", (siswa_id,))
            log_activity(user["id"], "HAPUS_SISWA", f"Guru menghapus siswa: {target['full_name']} ({target['username']})", conn=conn)

    return RedirectResponse(url="/guru/siswa?msg=Akun+siswa+telah+dihapus", status_code=status.HTTP_302_FOUND)

@router.post("/siswa/reset-password/{siswa_id}")
def reset_password_siswa(siswa_id: int, new_password: str = Form(...), user: dict = Depends(require_guru)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, username FROM users WHERE id = ? AND role = 'siswa'", (siswa_id,))
        target = cursor.fetchone()
        if target:
            pw_hash, salt = hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash = ?, salt = ?, must_change_password = 1 WHERE id = ?", (pw_hash, salt, siswa_id))
            log_activity(user["id"], "RESET_PASSWORD", f"Guru me-reset password siswa: {target['full_name']}", conn=conn)

    return RedirectResponse(url="/guru/siswa?msg=Password+siswa+berhasil+direset", status_code=status.HTTP_302_FOUND)

# Approve Reset Password Request from Student
@router.post("/siswa/reset-request/approve/{request_id}")
def approve_reset_request(
    request_id: int,
    temp_password: str = Form(""),
    user: dict = Depends(require_guru)
):
    # Jika guru tidak mengetik password sementara khusus, buatkan default KKA-2026 atau acak
    if not temp_password.strip():
        temp_password = "KKA-" + secrets.token_hex(2).upper()
    else:
        temp_password = temp_password.strip()

    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM password_reset_requests WHERE id = ?", (request_id,))
        req = cursor.fetchone()
        if not req:
            return RedirectResponse(url="/guru/siswa?err=Permintaan+reset+tidak+ditemukan", status_code=status.HTTP_302_FOUND)
        
        pw_hash, salt = hash_password(temp_password)
        # Update user password and set must_change_password = 1
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?, salt = ?, must_change_password = 1
            WHERE id = ?
        """, (pw_hash, salt, req["user_id"]))

        # Update request status
        cursor.execute("""
            UPDATE password_reset_requests
            SET status = 'approved', temp_password = ?, approved_at = CURRENT_TIMESTAMP, approved_by = ?
            WHERE id = ?
        """, (temp_password, user["id"], request_id))

        log_activity(user["id"], "APPROVE_RESET_PW", f"Guru menyetujui reset sandi siswa {req['full_name']} (@{req['username']}) dengan sandi sementara {temp_password}", conn=conn)

    return RedirectResponse(url=f"/guru/siswa?msg=Reset+password+disetujui!+Sandi+sementara:+{temp_password}", status_code=status.HTTP_302_FOUND)

@router.post("/siswa/reset-request/reject/{request_id}")
def reject_reset_request(request_id: int, user: dict = Depends(require_guru)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE password_reset_requests SET status = 'rejected' WHERE id = ?", (request_id,))
        log_activity(user["id"], "TOLAK_RESET_PW", f"Guru menolak permintaan reset password #{request_id}", conn=conn)

    return RedirectResponse(url="/guru/siswa?msg=Permintaan+reset+telah+ditolak", status_code=status.HTTP_302_FOUND)

# ==========================================
# GURU: DOWNLOAD FORMAT EXCEL & IMPORT EXCEL
# ==========================================
@router.get("/siswa/download-template")
def download_excel_template(user: dict = Depends(require_guru)):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Format Siswa KKA"

    # Header styling
    headers = ["Username / NISN", "Nama Lengkap Siswa", "Kelas", "Password Awal"]
    ws.append(headers)

    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center")
    
    for col_idx, col in enumerate(ws.iter_cols(min_row=1, max_row=1, min_col=1, max_col=4), start=1):
        cell = col[0]
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align

    # Sample rows
    sample_data = [
        ["1001", "Aditya Rizki Pratama", "X-1", "siswa123"],
        ["1002", "Bella Safitri", "X-1", "siswa123"],
        ["1003", "Cahyo Nugroho", "X-1", "siswa123"],
        ["1004", "Dinda Maharani", "X-2", "siswa123"],
        ["1005", "Eko Prasetyo", "X-2", "siswa123"],
    ]
    for row in sample_data:
        ws.append(row)

    # Set column widths
    column_widths = {'A': 20, 'B': 30, 'C': 12, 'D': 18}
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    # Save to buffer
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    log_activity(user["id"], "UNDUH_TEMPLATE_SISWA", "Guru mengunduh format template Excel tambah siswa")

    return Response(
        content=stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Format_Upload_Tambah_Siswa_KKA.xlsx"}
    )

@router.post("/siswa/import-excel")
async def import_excel_siswa(
    file: UploadFile = File(...),
    user: dict = Depends(require_guru)
):
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls") or file.filename.endswith(".csv")):
        return RedirectResponse(url="/guru/siswa?err=Format+file+harus+.xlsx+atau+.csv", status_code=status.HTTP_302_FOUND)

    contents = await file.read()
    added_count = 0
    skipped_count = 0

    try:
        if file.filename.endswith(".xlsx") or file.filename.endswith(".xls"):
            wb = openpyxl.load_workbook(io.BytesIO(contents), data_only=True)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            if len(rows) < 2:
                return RedirectResponse(url="/guru/siswa?err=File+Excel+kosong+atau+tidak+berisi+data", status_code=status.HTTP_302_FOUND)
            
            # Baris 1 adalah header, baris berikutnya data
            data_rows = rows[1:]
            with db_session() as conn:
                cursor = conn.cursor()
                for r in data_rows:
                    if not r or not r[0]:
                        continue
                    username = str(r[0]).strip()
                    full_name = str(r[1]).strip() if len(r) > 1 and r[1] else username
                    class_name = str(r[2]).strip() if len(r) > 2 and r[2] else "X-1"
                    plain_pass = str(r[3]).strip() if len(r) > 3 and r[3] else "siswa123"

                    # Check duplicate
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    if cursor.fetchone():
                        skipped_count += 1
                        continue

                    pw_hash, salt = hash_password(plain_pass)
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, salt, full_name, role, class_name)
                        VALUES (?, ?, ?, ?, 'siswa', ?)
                    """, (username, pw_hash, salt, full_name, class_name))
                    added_count += 1

                log_activity(user["id"], "IMPORT_EXCEL_SISWA", f"Import Excel: {added_count} siswa ditambahkan, {skipped_count} dilewati", conn=conn)

        else: # CSV fallback
            decoded = contents.decode("utf-8-sig")
            reader = csv.reader(io.StringIO(decoded))
            rows = list(reader)
            if len(rows) < 2:
                return RedirectResponse(url="/guru/siswa?err=File+CSV+kosong", status_code=status.HTTP_302_FOUND)
            data_rows = rows[1:]
            with db_session() as conn:
                cursor = conn.cursor()
                for r in data_rows:
                    if not r or not r[0]:
                        continue
                    username = r[0].strip()
                    full_name = r[1].strip() if len(r) > 1 else username
                    class_name = r[2].strip() if len(r) > 2 else "X-1"
                    plain_pass = r[3].strip() if len(r) > 3 else "siswa123"

                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    if cursor.fetchone():
                        skipped_count += 1
                        continue

                    pw_hash, salt = hash_password(plain_pass)
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, salt, full_name, role, class_name)
                        VALUES (?, ?, ?, ?, 'siswa', ?)
                    """, (username, pw_hash, salt, full_name, class_name))
                    added_count += 1

                log_activity(user["id"], "IMPORT_CSV_SISWA", f"Import CSV: {added_count} siswa ditambahkan", conn=conn)

    except Exception as e:
        return RedirectResponse(url=f"/guru/siswa?err=Gagal+membaca+file:+{str(e)}", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url=f"/guru/siswa?msg=Sukses!+{added_count}+siswa+berhasil+diimpor+dari+Excel+({skipped_count}+dilewati)", status_code=status.HTTP_302_FOUND)

# ==========================================
# GURU: KELOLA MATERI & UPLOAD SLIDE
# ==========================================
@router.get("/materi", response_class=HTMLResponse)
def kelola_materi_page(request: Request, user: dict = Depends(require_guru), msg: str = None, err: str = None):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM units ORDER BY unit_number ASC")
        units = [dict(u) for u in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM lessons ORDER BY meeting_number ASC")
        lessons = [dict(l) for l in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="guru/materi.html", context={
        "user": user,
        "active_nav": "materi",
        "units": units,
        "lessons": lessons,
        "msg": msg,
        "err": err
    })

@router.post("/materi/tambah")
def tambah_materi(
    request: Request,
    unit_id: int = Form(...),
    meeting_number: int = Form(...),
    title: str = Form(...),
    tp_focus: str = Form(...),
    narrative_title: str = Form(""),
    narrative_content: str = Form(""),
    content_html: str = Form(...),
    interactive_type: str = Form("none"),
    user: dict = Depends(require_guru)
):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lessons (unit_id, meeting_number, title, tp_focus, narrative_title, narrative_content, content_html, interactive_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (unit_id, meeting_number, title, tp_focus, narrative_title, narrative_content, content_html, interactive_type))
        
        log_activity(user["id"], "TAMBAH_MATERI", f"Guru menambah materi pertemuan {meeting_number}: {title}", conn=conn)

    return RedirectResponse(url="/guru/materi?msg=Materi+baru+berhasil+ditambahkan", status_code=status.HTTP_302_FOUND)

# Upload File Slide Materi
@router.post("/materi/upload-slide/{lesson_id}")
async def upload_slide_materi(
    lesson_id: int,
    file: UploadFile = File(...),
    user: dict = Depends(require_guru)
):
    if not file.filename:
        return RedirectResponse(url="/guru/materi?err=Tidak+ada+file+yang+dipilih", status_code=status.HTTP_302_FOUND)

    # Validasi ekstensi: PDF, PPT, PPTX
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".ppt", ".pptx", ".zip"]:
        return RedirectResponse(url="/guru/materi?err=Format+file+harus+PDF,+PPT,+atau+PPTX", status_code=status.HTTP_302_FOUND)

    # Simpan file ke SLIDES_DIR
    safe_filename = f"slide_p{lesson_id}_{secrets.token_hex(4)}{ext}"
    dest_path = SLIDES_DIR / safe_filename
    
    contents = await file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)

    rel_path = f"/uploads/slides/{safe_filename}"
    original_name = file.filename

    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE lessons
            SET slide_file_path = ?, slide_file_name = ?
            WHERE id = ?
        """, (rel_path, original_name, lesson_id))

        log_activity(user["id"], "UPLOAD_SLIDE", f"Guru mengunggah file slide '{original_name}' untuk materi #{lesson_id}", conn=conn)

    return RedirectResponse(url=f"/guru/materi?msg=File+slide+'{original_name}'+berhasil+diunggah!", status_code=status.HTTP_302_FOUND)

# ==========================================
# GURU: KELOLA KUIS & SOAL
# ==========================================
@router.get("/kuis", response_class=HTMLResponse)
def kelola_kuis_page(request: Request, user: dict = Depends(require_guru), msg: str = None):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT q.*, u.title as unit_title,
                   (SELECT COUNT(*) FROM quiz_questions WHERE quiz_id = q.id) as question_count,
                   (SELECT COUNT(*) FROM quiz_attempts WHERE quiz_id = q.id) as attempts_count,
                   (SELECT AVG(score) FROM quiz_attempts WHERE quiz_id = q.id) as avg_score
            FROM quizzes q
            JOIN units u ON q.unit_id = u.id
            ORDER BY q.id ASC
        """)
        quizzes = [dict(q) for q in cursor.fetchall()]

        cursor.execute("SELECT * FROM quiz_questions ORDER BY quiz_id ASC, order_num ASC")
        questions = [dict(q) for q in cursor.fetchall()]

        cursor.execute("""
            SELECT r.*, u.full_name, u.username, u.class_name, q.title as quiz_title
            FROM quiz_remedial_requests r
            JOIN users u ON r.user_id = u.id
            JOIN quizzes q ON r.quiz_id = q.id
            ORDER BY r.created_at DESC
        """)
        remedial_requests = [dict(r) for r in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="guru/kuis.html", context={
        "user": user,
        "active_nav": "kuis",
        "quizzes": quizzes,
        "questions": questions,
        "remedial_requests": remedial_requests,
        "msg": msg
    })

@router.post("/kuis/tambah-soal")
def tambah_soal_kuis(
    request: Request,
    quiz_id: int = Form(...),
    question_text: str = Form(...),
    option_a: str = Form(...),
    option_b: str = Form(...),
    option_c: str = Form(...),
    option_d: str = Form(...),
    option_e: str = Form(""),
    correct_option: str = Form(...),
    explanation: str = Form(""),
    user: dict = Depends(require_guru)
):
    with db_session() as conn:
        cursor = conn.cursor()
        order_num = cursor.execute("SELECT COUNT(*) as c FROM quiz_questions WHERE quiz_id = ?", (quiz_id,)).fetchone()["c"] + 1
        cursor.execute("""
            INSERT INTO quiz_questions (quiz_id, question_text, option_a, option_b, option_c, option_d, option_e, correct_option, explanation, order_num)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (quiz_id, question_text, option_a, option_b, option_c, option_d, option_e, correct_option, explanation, order_num))
        
        log_activity(user["id"], "TAMBAH_SOAL", f"Guru menambah butir soal ke kuis ID #{quiz_id}", conn=conn)

    return RedirectResponse(url="/guru/kuis?msg=Soal+baru+berhasil+ditambahkan", status_code=status.HTTP_302_FOUND)

@router.post("/kuis/remedial/{request_id}/approve")
def approve_remedial(request_id: int, teacher_notes: str = Form(""), user: dict = Depends(require_guru)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE quiz_remedial_requests 
            SET status = 'approved', teacher_notes = ?, reviewed_at = CURRENT_TIMESTAMP, reviewed_by = ?
            WHERE id = ?
        """, (teacher_notes, user["id"], request_id))
        log_activity(user["id"], "SETUJUI_REMEDIAL", f"Guru menyetujui permohonan remedial ID #{request_id} (Diberi 1x kesempatan)", conn=conn)

    return RedirectResponse(url="/guru/kuis?msg=Permohonan+remedial+berhasil+disetujui!+Siswa+diberikan+1x+kesempatan+mengulang+ujian.", status_code=status.HTTP_302_FOUND)

@router.post("/kuis/remedial/{request_id}/reject")
def reject_remedial(request_id: int, teacher_notes: str = Form(""), user: dict = Depends(require_guru)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE quiz_remedial_requests 
            SET status = 'rejected', teacher_notes = ?, reviewed_at = CURRENT_TIMESTAMP, reviewed_by = ?
            WHERE id = ?
        """, (teacher_notes, user["id"], request_id))
        log_activity(user["id"], "TOLAK_REMEDIAL", f"Guru menolak permohonan remedial ID #{request_id}", conn=conn)

    return RedirectResponse(url="/guru/kuis?msg=Permohonan+remedial+ditolak.", status_code=status.HTTP_302_FOUND)

# ==========================================
# GURU: KELOLA TUGAS / LKPD
# ==========================================
@router.get("/tugas", response_class=HTMLResponse)
def kelola_tugas_page(request: Request, user: dict = Depends(require_guru), msg: str = None):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, 
                   (SELECT COUNT(*) FROM submissions WHERE assignment_id = a.id) as submission_count
            FROM assignments a
            ORDER BY a.meeting_number ASC
        """)
        assignments = [dict(a) for a in cursor.fetchall()]

        cursor.execute("""
            SELECT s.*, a.title as assignment_title, u.full_name as student_name, u.class_name
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.id
            JOIN users u ON s.user_id = u.id
            ORDER BY s.submitted_at DESC
        """)
        submissions = [dict(s) for s in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="guru/tugas.html", context={
        "user": user,
        "active_nav": "tugas",
        "assignments": assignments,
        "submissions": submissions,
        "msg": msg
    })

@router.post("/tugas/nilai/{submission_id}")
def beri_nilai_tugas(
    submission_id: int,
    score: int = Form(...),
    feedback: str = Form(""),
    user: dict = Depends(require_guru)
):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE submissions
            SET score = ?, feedback = ?, status = 'graded', graded_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (score, feedback, submission_id))
        
        log_activity(user["id"], "NILAI_TUGAS", f"Guru menilai pengumpulan tugas #{submission_id} dengan skor {score}", conn=conn)

    return RedirectResponse(url="/guru/tugas?msg=Nilai+dan+umpan+balik+telah+tersimpan", status_code=status.HTTP_302_FOUND)

# ==========================================
# GURU: LAPORAN AKTIVITAS & EKSPOR
# ==========================================
@router.get("/laporan", response_class=HTMLResponse)
def laporan_aktivitas_page(request: Request, user: dict = Depends(require_guru)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.id, l.action, l.details, l.created_at, l.ip_address, u.full_name, u.role, u.class_name, u.username
            FROM activity_logs l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.created_at DESC
            LIMIT 200
        """)
        logs = [dict(l) for l in cursor.fetchall()]

        cursor.execute("""
            SELECT u.id, u.username, u.full_name, u.class_name,
                (SELECT COUNT(*) FROM activity_logs WHERE user_id = u.id) as total_interactions,
                (SELECT MAX(created_at) FROM activity_logs WHERE user_id = u.id AND action = 'LOGIN') as last_login,
                (SELECT AVG(score) FROM quiz_attempts WHERE user_id = u.id) as avg_quiz,
                (SELECT COUNT(*) FROM quiz_attempts WHERE user_id = u.id) as completed_quizzes,
                (SELECT COUNT(*) FROM submissions WHERE user_id = u.id) as completed_assignments,
                (SELECT COUNT(*) FROM reflections WHERE user_id = u.id) as completed_reflections
            FROM users u
            WHERE u.role = 'siswa'
            ORDER BY u.full_name ASC
        """)
        students_summary = [dict(s) for s in cursor.fetchall()]

        # Survey Refleksi Siswa
        cursor.execute("""
            SELECT r.*, u.full_name, u.username, u.class_name
            FROM reflections r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.submitted_at DESC
        """)
        reflections_list = [dict(r) for r in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="guru/laporan.html", context={
        "user": user,
        "active_nav": "laporan",
        "logs": logs,
        "students_summary": students_summary,
        "reflections_list": reflections_list
    })

@router.get("/laporan/export-csv")
def export_laporan_csv(user: dict = Depends(require_guru)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID Siswa", "Username", "Nama Lengkap", "Kelas", "Rata-rata Kuis", "Jumlah Kuis Selesai", "Jumlah LKPD Dikumpul", "Jumlah Refleksi", "Total Interaksi", "Login Terakhir"])
    
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.full_name, u.class_name,
                (SELECT AVG(score) FROM quiz_attempts WHERE user_id = u.id) as avg_quiz,
                (SELECT COUNT(*) FROM quiz_attempts WHERE user_id = u.id) as completed_quizzes,
                (SELECT COUNT(*) FROM submissions WHERE user_id = u.id) as completed_assignments,
                (SELECT COUNT(*) FROM reflections WHERE user_id = u.id) as completed_reflections,
                (SELECT COUNT(*) FROM activity_logs WHERE user_id = u.id) as total_interactions,
                (SELECT MAX(created_at) FROM activity_logs WHERE user_id = u.id AND action = 'LOGIN') as last_login
            FROM users u
            WHERE u.role = 'siswa'
            ORDER BY u.full_name ASC
        """)
        for s in cursor.fetchall():
            avg_q = round(s["avg_quiz"], 1) if s["avg_quiz"] is not None else 0
            writer.writerow([
                s["id"], s["username"], s["full_name"], s["class_name"],
                avg_q, s["completed_quizzes"], s["completed_assignments"],
                s["completed_reflections"], s["total_interactions"], s["last_login"] or "-"
            ])

        log_activity(user["id"], "EXPORT_CSV", "Guru mengekspor laporan aktivitas ke file CSV", conn=conn)
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rekap_aktivitas_siswa_kka_fase_e.csv"}
    )
