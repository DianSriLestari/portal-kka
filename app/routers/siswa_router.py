from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import json
from app.config import TEMPLATES_DIR
from app.database import db_session, log_activity, get_student_progression
from app.auth import hash_password
from app.dependencies import require_siswa, require_login

router = APIRouter(prefix="/siswa")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("", response_class=HTMLResponse)
def siswa_dashboard(request: Request, user: dict = Depends(require_siswa), msg: str = None, err: str = None):
    with db_session() as conn:
        cursor = conn.cursor()
        
        # Unit 1 info
        cursor.execute("SELECT * FROM units WHERE unit_number = 1")
        unit = dict(cursor.fetchone())

        # Lessons in Unit 1
        cursor.execute("SELECT * FROM lessons WHERE unit_id = ? ORDER BY meeting_number ASC", (unit["id"],))
        lessons = [dict(l) for l in cursor.fetchall()]

        # Quizzes
        cursor.execute("""
            SELECT q.*, 
                   (SELECT score FROM quiz_attempts WHERE quiz_id = q.id AND user_id = ? ORDER BY completed_at DESC LIMIT 1) as my_score
            FROM quizzes q
            WHERE q.unit_id = ?
            ORDER BY q.meeting_number ASC
        """, (user["id"], unit["id"]))
        quizzes = [dict(q) for q in cursor.fetchall()]

        # Assignments
        cursor.execute("""
            SELECT a.*, 
                   (SELECT status FROM submissions WHERE assignment_id = a.id AND user_id = ?) as my_status,
                   (SELECT score FROM submissions WHERE assignment_id = a.id AND user_id = ?) as my_score
            FROM assignments a
            WHERE a.unit_id = ?
            ORDER BY a.meeting_number ASC
        """, (user["id"], user["id"], unit["id"]))
        assignments = [dict(a) for a in cursor.fetchall()]

        # Check must_change_password
        cursor.execute("SELECT must_change_password FROM users WHERE id = ?", (user["id"],))
        must_change_row = cursor.fetchone()
        must_change = must_change_row["must_change_password"] if must_change_row else 0

        # HITUNG PROGRESS BERURUTAN (PRASYARAT PERTEMUAN)
        progression = get_student_progression(user["id"], conn)

    return templates.TemplateResponse(request=request, name="siswa/dashboard.html", context={
        "user": user,
        "active_nav": "dashboard",
        "unit": unit,
        "lessons": lessons,
        "quizzes": quizzes,
        "assignments": assignments,
        "progression": progression,
        "must_change": must_change,
        "msg": msg,
        "err": err
    })

# ==========================================
# GANTI PASSWORD SISWA
# ==========================================
@router.get("/ganti-password", response_class=HTMLResponse)
def ganti_password_page(request: Request, user: dict = Depends(require_siswa), notice: str = None):
    err = "Anda sedang menggunakan kata sandi sementara. Demi keamanan, silakan tentukan kata sandi baru Anda sekarang." if notice == "temp_pw" else None
    return templates.TemplateResponse(request=request, name="siswa/ganti_password.html", context={
        "user": user,
        "active_nav": "dashboard",
        "err": err,
        "msg": None
    })

@router.post("/ganti-password")
def submit_ganti_password(
    request: Request,
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    user: dict = Depends(require_siswa)
):
    if new_password != confirm_password:
        return templates.TemplateResponse(request=request, name="siswa/ganti_password.html", context={
            "user": user,
            "active_nav": "dashboard",
            "err": "Konfirmasi kata sandi tidak cocok. Harap ketik ulang dengan benar.",
            "msg": None
        }, status_code=400)

    if len(new_password) < 4:
        return templates.TemplateResponse(request=request, name="siswa/ganti_password.html", context={
            "user": user,
            "active_nav": "dashboard",
            "err": "Kata sandi minimal 4 karakter.",
            "msg": None
        }, status_code=400)

    with db_session() as conn:
        cursor = conn.cursor()
        pw_hash, salt = hash_password(new_password)
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?, salt = ?, must_change_password = 0 
            WHERE id = ?
        """, (pw_hash, salt, user["id"]))

        cursor.execute("""
            UPDATE password_reset_requests 
            SET status = 'completed' 
            WHERE user_id = ? AND status = 'approved'
        """, (user["id"],))

        log_activity(user["id"], "GANTI_PASSWORD", f"Siswa {user['full_name']} berhasil memperbarui kata sandi baru", conn=conn)

    return RedirectResponse(url="/siswa?msg=Kata+sandi+baru+berhasil+disimpan.+Selamat+belajar!", status_code=status.HTTP_302_FOUND)

# ==========================================
# SISWA: MODUL PEMBELAJARAN TERPADU
# ==========================================
@router.get("/modul/{lesson_id}", response_class=HTMLResponse)
def baca_modul(lesson_id: int, request: Request, tab: str = "materi", user: dict = Depends(require_login), msg: str = None, err: str = None):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,))
        lesson = cursor.fetchone()
        if not lesson:
            raise HTTPException(status_code=404, detail="Materi tidak ditemukan")
        lesson = dict(lesson)

        # VALIDASI PRASYARAT UNTUK SISWA
        if user["role"] == "siswa":
            progression = get_student_progression(user["id"], conn)
            m_num = lesson["meeting_number"]
            if m_num == 2 and not progression["p1"]["completed"]:
                return RedirectResponse(
                    url="/siswa?err=Pertemuan+2+masih+terkunci.+Harap+selesaikan+seluruh+rangkaian+aktivitas+Pertemuan+1+terlebih+dahulu.",
                    status_code=status.HTTP_302_FOUND
                )
            elif m_num == 3 and not progression["p2"]["completed"]:
                return RedirectResponse(
                    url="/siswa?err=Pertemuan+3+masih+terkunci.+Harap+selesaikan+seluruh+rangkaian+aktivitas+Pertemuan+2+terlebih+dahulu.",
                    status_code=status.HTTP_302_FOUND
                )

        # Catat pembacaan materi modul
        log_activity(user["id"], "BACA_MODUL", f"{user['role'].capitalize()} {user['full_name']} membuka materi: {lesson['title']}", conn=conn)

        # Ambil LKPD terintegrasi untuk pertemuan ini
        cursor.execute("SELECT * FROM assignments WHERE meeting_number = ?", (lesson["meeting_number"],))
        assignment = cursor.fetchone()
        assignment = dict(assignment) if assignment else None

        # Ambil status pengumpulan LKPD siswa jika ada
        submission = None
        if assignment and user["role"] == "siswa":
            cursor.execute("SELECT * FROM submissions WHERE assignment_id = ? AND user_id = ?", (assignment["id"], user["id"]))
            sub_row = cursor.fetchone()
            submission = dict(sub_row) if sub_row else None

        # Ambil Kuis terintegrasi untuk pertemuan ini
        cursor.execute("SELECT * FROM quizzes WHERE meeting_number = ? ORDER BY id ASC LIMIT 1", (lesson["meeting_number"],))
        quiz = cursor.fetchone()
        quiz = dict(quiz) if quiz else None

        quiz_attempt = None
        if quiz and user["role"] == "siswa":
            cursor.execute("SELECT * FROM quiz_attempts WHERE quiz_id = ? AND user_id = ? ORDER BY completed_at DESC LIMIT 1", (quiz["id"], user["id"]))
            qa_row = cursor.fetchone()
            quiz_attempt = dict(qa_row) if qa_row else None

        # Ambil progres simulasi pertemuan ini
        sim_done = False
        if lesson["interactive_type"] != "none" and user["role"] == "siswa":
            cursor.execute("SELECT completed FROM interactive_progress WHERE user_id = ? AND activity_key = ?", (user["id"], lesson["interactive_type"]))
            sp_row = cursor.fetchone()
            sim_done = sp_row["completed"] == 1 if sp_row else False
            if not sim_done:
                cursor.execute("SELECT COUNT(*) as c FROM activity_logs WHERE user_id = ? AND action = 'LAB_SIMULASI' AND (details LIKE ? OR details LIKE ?)", (user["id"], f"%{lesson['interactive_type']}%", f"%{lesson['title']}%"))
                sim_done = cursor.fetchone()["c"] > 0

        # Status checklist pertemuan ini
        progression = get_student_progression(user["id"], conn) if user["role"] == "siswa" else None

    return templates.TemplateResponse(request=request, name="siswa/modul.html", context={
        "user": user,
        "active_nav": "dashboard",
        "lesson": lesson,
        "active_tab": tab,
        "assignment": assignment,
        "submission": submission,
        "quiz": quiz,
        "quiz_attempt": quiz_attempt,
        "sim_done": sim_done,
        "progression": progression,
        "msg": msg,
        "err": err
    })

# Akses Slide Presentasi & Tandai Selesai
@router.get("/modul/{lesson_id}/slide")
def akses_slide_materi(lesson_id: int, user: dict = Depends(require_login)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, slide_file_path, slide_file_name FROM lessons WHERE id = ?", (lesson_id,))
        lesson = cursor.fetchone()
        if not lesson or not lesson["slide_file_path"]:
            raise HTTPException(status_code=404, detail="File slide belum diunggah oleh guru.")
        
        log_activity(user["id"], "BACA_SLIDE", f"Siswa mengakses slide bahan tayang: {lesson['title']}", conn=conn)
        return RedirectResponse(url=lesson["slide_file_path"], status_code=status.HTTP_302_FOUND)

# Tandai Selesai Membaca Materi Konsep
@router.post("/modul/{lesson_id}/tandai-materi")
def tandai_materi_selesai(lesson_id: int, user: dict = Depends(require_siswa)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM lessons WHERE id = ?", (lesson_id,))
        lesson = cursor.fetchone()
        log_activity(user["id"], "BACA_MODUL", f"Siswa menandai selesai membaca materi: {lesson['title']}", conn=conn)
        log_activity(user["id"], "BACA_SLIDE", f"Siswa menandai selesai mempelajari slide: {lesson['title']}", conn=conn)

    return RedirectResponse(url=f"/siswa/modul/{lesson_id}?tab=simulasi&msg=Bagus!+Materi+dan+slide+telah+ditandai+selesai.+Lanjutkan+ke+Lab+Simulasi.", status_code=status.HTTP_302_FOUND)

# Tandai Selesai Simulasi dari dalam modul
@router.post("/simulasi/selesai/{activity_key}")
def tandai_simulasi_selesai(activity_key: str, lesson_id: int = Form(1), user: dict = Depends(require_siswa)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO interactive_progress (user_id, unit_id, activity_key, score, completed, updated_at)
            VALUES (?, 1, ?, 100, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, unit_id, activity_key) DO UPDATE SET
                score = 100,
                completed = 1,
                updated_at = CURRENT_TIMESTAMP
        """, (user["id"], activity_key))

        log_activity(user["id"], "LAB_SIMULASI", f"Siswa menyelesaikan lab simulasi: {activity_key}", conn=conn)

    return RedirectResponse(url=f"/siswa/modul/{lesson_id}?tab=lkpd&msg=Hebat!+Simulasi+telah+selesai.+Sekarang+kerjakan+LKPD+kelompokmu.", status_code=status.HTTP_302_FOUND)

# Submit LKPD dari dalam modul terintegrasi
@router.post("/modul/{lesson_id}/submit-lkpd")
def submit_lkpd_dalam_modul(
    lesson_id: int,
    assignment_id: int = Form(...),
    group_members: str = Form(""),
    submission_text: str = Form(...),
    user: dict = Depends(require_siswa)
):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM submissions WHERE assignment_id = ? AND user_id = ?", (assignment_id, user["id"]))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE submissions 
                SET group_members = ?, submission_text = ?, submitted_at = CURRENT_TIMESTAMP, status = 'submitted'
                WHERE id = ?
            """, (group_members, submission_text, existing["id"]))
        else:
            cursor.execute("""
                INSERT INTO submissions (assignment_id, user_id, group_members, submission_text, status)
                VALUES (?, ?, ?, ?, 'submitted')
            """, (assignment_id, user["id"], group_members, submission_text))

        log_activity(user["id"], "KUMPUL_TUGAS", f"Siswa mengumpulkan LKPD #{assignment_id} pada materi #{lesson_id}", conn=conn)

    return RedirectResponse(url=f"/siswa/modul/{lesson_id}?tab=evaluasi&msg=Laporan+LKPD+berhasil+dikirimkan+ke+Guru!+Lanjutkan+ke+sub-materi+kuis/evaluasi.", status_code=status.HTTP_302_FOUND)

@router.post("/modul/{lesson_id}/submit-lkpd-ajax")
async def submit_lkpd_ajax(
    lesson_id: int,
    request: Request,
    user: dict = Depends(require_siswa)
):
    try:
        body = await request.json()
        assignment_id = int(body.get("assignment_id", 3))
        group_members = body.get("group_members", "")
        submission_text = body.get("submission_text", "")
    except Exception:
        form = await request.form()
        assignment_id = int(form.get("assignment_id", 3))
        group_members = form.get("group_members", "")
        submission_text = form.get("submission_text", "")

    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM submissions WHERE assignment_id = ? AND user_id = ?", (assignment_id, user["id"]))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE submissions 
                SET group_members = ?, submission_text = ?, submitted_at = CURRENT_TIMESTAMP, status = 'submitted'
                WHERE id = ?
            """, (group_members, submission_text, existing["id"]))
        else:
            cursor.execute("""
                INSERT INTO submissions (assignment_id, user_id, group_members, submission_text, status)
                VALUES (?, ?, ?, ?, 'submitted')
            """, (assignment_id, user["id"], group_members, submission_text))

        log_activity(user["id"], "KUMPUL_TUGAS", f"Siswa mengumpulkan tugas LKPD #{assignment_id} materi #{lesson_id} (Interaktif)", conn=conn)

    return {"status": "success", "message": "Jawaban LKPD berhasil disimpan dan terkirim ke Guru!"}

# ==========================================
# SISWA: LAB SIMULASI HUB & DETAIL
# ==========================================
@router.get("/simulasi", response_class=HTMLResponse)
def lab_simulasi_hub(request: Request, user: dict = Depends(require_siswa), msg: str = None, err: str = None):
    with db_session() as conn:
        progression = get_student_progression(user["id"], conn)
        
    return templates.TemplateResponse(request=request, name="siswa/simulasi_hub.html", context={
        "user": user,
        "active_nav": "simulasi",
        "progression": progression,
        "msg": msg,
        "err": err
    })

@router.get("/simulasi/{activity_key}", response_class=HTMLResponse)
def buka_simulasi_spesifik(activity_key: str, request: Request, user: dict = Depends(require_login)):
    valid_sims = {
        "pohon_dekomposisi": {"template": "siswa/simulasi_pohon_dekomposisi.html", "meeting": 1, "title": "Pohon Dekomposisi"},
        "peta_abstraksi": {"template": "siswa/simulasi_peta_abstraksi.html", "meeting": 2, "title": "Peta Abstraksi"},
        "dry_run_simulator": {"template": "siswa/simulasi_dry_run_simulator.html", "meeting": 3, "title": "Dry-Run Simulator Kasir"}
    }
    if activity_key not in valid_sims:
        raise HTTPException(status_code=404, detail="Simulasi tidak ditemukan")
        
    sim_info = valid_sims[activity_key]
    with db_session() as conn:
        if user["role"] == "siswa":
            progression = get_student_progression(user["id"], conn)
            if sim_info["meeting"] == 2 and not progression["p2"]["unlocked"]:
                return RedirectResponse(url="/siswa/simulasi?err=Simulasi+2+masih+terkunci.+Selesaikan+rangkaian+Pertemuan+1+terlebih+dahulu.", status_code=status.HTTP_302_FOUND)
            elif sim_info["meeting"] == 3 and not progression["p3"]["unlocked"]:
                return RedirectResponse(url="/siswa/simulasi?err=Simulasi+3+masih+terkunci.+Selesaikan+rangkaian+Pertemuan+2+terlebih+dahulu.", status_code=status.HTTP_302_FOUND)

        log_activity(user["id"], "LAB_SIMULASI", f"Siswa mengakses lab: {sim_info['title']}", conn=conn)

    return templates.TemplateResponse(request=request, name=sim_info["template"], context={
        "user": user,
        "active_nav": "simulasi",
        "lesson_id": sim_info["meeting"]
    })

# ==========================================
# SISWA: DAFTAR TUGAS LKPD
# ==========================================
@router.get("/tugas", response_class=HTMLResponse)
def daftar_tugas(request: Request, user: dict = Depends(require_siswa), msg: str = None, err: str = None):
    with db_session() as conn:
        cursor = conn.cursor()
        progression = get_student_progression(user["id"], conn)
        cursor.execute("SELECT * FROM assignments ORDER BY meeting_number ASC")
        raw_assignments = [dict(a) for a in cursor.fetchall()]
        
        assignments = []
        for a in raw_assignments:
            cursor.execute("SELECT * FROM submissions WHERE assignment_id = ? AND user_id = ?", (a["id"], user["id"]))
            sub = cursor.fetchone()
            a["sub_status"] = sub["status"] if sub else None
            a["sub_score"] = sub["score"] if sub else None
            a["sub_feedback"] = sub["feedback"] if sub else None
            a["sub_members"] = sub["group_members"] if sub else None
            a["sub_text"] = sub["submission_text"] if sub else None
            
            m = a["meeting_number"]
            if m == 2:
                a["is_unlocked"] = progression["p2"]["unlocked"]
            elif m == 3:
                a["is_unlocked"] = progression["p3"]["unlocked"]
            else:
                a["is_unlocked"] = True
                
            assignments.append(a)

    return templates.TemplateResponse(request=request, name="siswa/tugas_list.html", context={
        "user": user,
        "active_nav": "tugas",
        "assignments": assignments,
        "progression": progression,
        "msg": msg,
        "err": err
    })

@router.post("/tugas/submit/{assignment_id}")
def submit_tugas_standalone(
    assignment_id: int,
    group_members: str = Form(""),
    submission_text: str = Form(...),
    user: dict = Depends(require_siswa)
):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,))
        assignment = cursor.fetchone()
        if not assignment:
            raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
        
        progression = get_student_progression(user["id"], conn)
        m = assignment["meeting_number"]
        if m == 2 and not progression["p2"]["unlocked"]:
            return RedirectResponse(url="/siswa/tugas?err=LKPD+2+masih+terkunci.+Selesaikan+Pertemuan+1+terlebih+dahulu.", status_code=status.HTTP_302_FOUND)
        elif m == 3 and not progression["p3"]["unlocked"]:
            return RedirectResponse(url="/siswa/tugas?err=LKPD+3+masih+terkunci.+Selesaikan+Pertemuan+2+terlebih+dahulu.", status_code=status.HTTP_302_FOUND)

        cursor.execute("SELECT id FROM submissions WHERE assignment_id = ? AND user_id = ?", (assignment_id, user["id"]))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE submissions 
                SET group_members = ?, submission_text = ?, submitted_at = CURRENT_TIMESTAMP, status = 'submitted'
                WHERE id = ?
            """, (group_members, submission_text, existing["id"]))
        else:
            cursor.execute("""
                INSERT INTO submissions (assignment_id, user_id, group_members, submission_text, status)
                VALUES (?, ?, ?, ?, 'submitted')
            """, (assignment_id, user["id"], group_members, submission_text))

        log_activity(user["id"], "KUMPUL_TUGAS", f"Siswa mengumpulkan {assignment['title']}", conn=conn)

    return RedirectResponse(url="/siswa/tugas?msg=Tugas+LKPD+berhasil+dikirimkan+ke+Guru!", status_code=status.HTTP_302_FOUND)

# ==========================================
# SISWA: KUIS & UJIAN EVALUASI (DENGAN PRASYARAT)
# ==========================================
@router.get("/kuis/{quiz_id}", response_class=HTMLResponse)
def kerjakan_kuis(quiz_id: int, request: Request, user: dict = Depends(require_siswa)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        quiz = cursor.fetchone()
        if not quiz:
            raise HTTPException(status_code=404, detail="Kuis tidak ditemukan")
        quiz = dict(quiz)

        is_remedial_session = False

        # VALIDASI PRASYARAT UJIAN SUMATIF
        if quiz["quiz_type"] == "ujian":
            progression = get_student_progression(user["id"], conn)
            if not progression["eval"]["unlocked"]:
                return RedirectResponse(
                    url="/siswa?err=Ujian+Sumatif+masih+terkunci.+Selesaikan+seluruh+rangkaian+Pertemuan+1,+2,+dan+3+terlebih+dahulu.",
                    status_code=status.HTTP_302_FOUND
                )

            # Cek riwayat pengerjaan ujian siswa (aturan 1x pengerjaan & remedial)
            cursor.execute("SELECT * FROM quiz_attempts WHERE user_id = ? AND quiz_id = ? ORDER BY id DESC", (user["id"], quiz_id))
            attempts = [dict(a) for a in cursor.fetchall()]

            if len(attempts) >= 1:
                last_attempt = attempts[0]
                if last_attempt["score"] > 75:
                    return RedirectResponse(
                        url=f"/siswa/kuis/{quiz_id}/hasil?msg=Selamat!+Anda+sudah+menyelesaikan+ujian+ini+dan+dinyatakan+LULUS+KKM+(Skor:+{last_attempt['score']}).",
                        status_code=status.HTTP_302_FOUND
                    )
                
                # Jika skor <= 75, periksa izin perbaikan (remedial) dari guru
                cursor.execute("""
                    SELECT * FROM quiz_remedial_requests 
                    WHERE user_id = ? AND quiz_id = ? 
                    ORDER BY id DESC LIMIT 1
                """, (user["id"], quiz_id))
                remedial = cursor.fetchone()
                remedial = dict(remedial) if remedial else None

                if not remedial:
                    return RedirectResponse(
                        url=f"/siswa/kuis/{quiz_id}/hasil?err=Ujian+hanya+dapat+dikerjakan+1+kali.+Nilai+Anda+belum+mencapai+KKM+(>75).+Silakan+ajukan+permohonan+perbaikan+kepada+Guru.",
                        status_code=status.HTTP_302_FOUND
                    )
                elif remedial["status"] == "pending":
                    return RedirectResponse(
                        url=f"/siswa/kuis/{quiz_id}/hasil?err=Permohonan+perbaikan+sedang+menunggu+persetujuan+Guru.",
                        status_code=status.HTTP_302_FOUND
                    )
                elif remedial["status"] == "rejected":
                    return RedirectResponse(
                        url=f"/siswa/kuis/{quiz_id}/hasil?err=Permohonan+perbaikan+tidak+disetujui+oleh+Guru.",
                        status_code=status.HTTP_302_FOUND
                    )
                elif remedial["status"] == "approved":
                    if remedial["used"] >= 1 or len(attempts) >= 2:
                        return RedirectResponse(
                            url=f"/siswa/kuis/{quiz_id}/hasil?err=Anda+telah+menggunakan+seluruh+kesempatan+ujian+perbaikan+(maksimal+2+kali).",
                            status_code=status.HTTP_302_FOUND
                        )
                    # Diizinkan mengerjakan kesempatan ke-2 (remedial)
                    is_remedial_session = True

        cursor.execute("SELECT id, question_text, option_a, option_b, option_c, option_d, option_e, order_num FROM quiz_questions WHERE quiz_id = ? ORDER BY order_num ASC", (quiz_id,))
        questions = [dict(q) for q in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="siswa/kuis_pengerjaan.html", context={
        "user": user,
        "active_nav": "dashboard",
        "quiz": quiz,
        "questions": questions,
        "is_remedial_session": is_remedial_session
    })

@router.post("/kuis/{quiz_id}/submit")
async def submit_kuis(quiz_id: int, request: Request, user: dict = Depends(require_siswa)):
    form_data = await request.form()
    
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        quiz = dict(cursor.fetchone())

        # Validasi batas percobaan ujian sumatif
        if quiz["quiz_type"] == "ujian":
            cursor.execute("SELECT * FROM quiz_attempts WHERE user_id = ? AND quiz_id = ? ORDER BY id DESC", (user["id"], quiz_id))
            existing_attempts = cursor.fetchall()
            if len(existing_attempts) >= 1:
                cursor.execute("""
                    SELECT * FROM quiz_remedial_requests 
                    WHERE user_id = ? AND quiz_id = ? AND status = 'approved' AND used = 0
                    ORDER BY id DESC LIMIT 1
                """, (user["id"], quiz_id))
                rem_req = cursor.fetchone()
                if not rem_req or len(existing_attempts) >= 2:
                    return RedirectResponse(
                        url=f"/siswa/kuis/{quiz_id}/hasil?err=Batas+maksimal+pengerjaan+ujian+telah+habis.",
                        status_code=status.HTTP_302_FOUND
                    )
                # Tandai kesempatan remedial telah digunakan
                cursor.execute("UPDATE quiz_remedial_requests SET used = 1 WHERE id = ?", (rem_req["id"],))

        cursor.execute("SELECT id, correct_option FROM quiz_questions WHERE quiz_id = ?", (quiz_id,))
        questions = cursor.fetchall()
        
        total_q = len(questions)
        correct_c = 0
        answers = {}

        for q in questions:
            qid = str(q["id"])
            user_ans = form_data.get(f"q_{qid}")
            answers[qid] = user_ans
            if user_ans and user_ans.strip().upper() == q["correct_option"].strip().upper():
                correct_c += 1

        score = int((correct_c / total_q) * 100) if total_q > 0 else 0

        cursor.execute("""
            INSERT INTO quiz_attempts (quiz_id, user_id, score, total_questions, correct_answers, answers_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (quiz_id, user["id"], score, total_q, correct_c, json.dumps(answers)))

        log_activity(user["id"], "KERJAKAN_KUIS", f"Siswa menyelesaikan {quiz['quiz_type']} '{quiz['title']}' dengan nilai {score}", conn=conn)

    return RedirectResponse(url=f"/siswa/kuis/{quiz_id}/hasil?score={score}&total={total_q}&correct={correct_c}", status_code=status.HTTP_302_FOUND)

@router.get("/kuis/{quiz_id}/hasil", response_class=HTMLResponse)
def hasil_kuis(
    quiz_id: int,
    request: Request,
    score: Optional[int] = None,
    total: Optional[int] = None,
    correct: Optional[int] = None,
    msg: Optional[str] = None,
    err: Optional[str] = None,
    user: dict = Depends(require_siswa)
):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        quiz = cursor.fetchone()
        if not quiz:
            raise HTTPException(status_code=404, detail="Kuis tidak ditemukan")
        quiz = dict(quiz)

        # Jika score/total/correct tidak ada di parameter URL, ambil dari attempt terakhir
        cursor.execute("SELECT * FROM quiz_attempts WHERE user_id = ? AND quiz_id = ? ORDER BY id DESC LIMIT 1", (user["id"], quiz_id))
        latest_attempt = cursor.fetchone()
        if latest_attempt:
            if score is None:
                score = latest_attempt["score"]
            if total is None:
                total = latest_attempt["total_questions"]
            if correct is None:
                correct = latest_attempt["correct_answers"]
        else:
            if score is None:
                score = 0
            if total is None:
                total = 0
            if correct is None:
                correct = 0

        # Ambil total percobaan yang sudah dilakukan
        attempts_count = cursor.execute("SELECT COUNT(*) as c FROM quiz_attempts WHERE user_id = ? AND quiz_id = ?", (user["id"], quiz_id)).fetchone()["c"]

        # Ambil permohonan remedial terakhir
        cursor.execute("SELECT * FROM quiz_remedial_requests WHERE user_id = ? AND quiz_id = ? ORDER BY id DESC LIMIT 1", (user["id"], quiz_id))
        remedial_req = cursor.fetchone()
        remedial_req = dict(remedial_req) if remedial_req else None

    return templates.TemplateResponse(request=request, name="siswa/kuis_hasil.html", context={
        "user": user,
        "active_nav": "dashboard",
        "quiz": quiz,
        "score": score,
        "total": total,
        "correct": correct,
        "attempts_count": attempts_count,
        "remedial_req": remedial_req,
        "msg": msg,
        "err": err
    })

@router.post("/kuis/{quiz_id}/remedial-request")
def ajukan_remedial(
    quiz_id: int,
    request: Request,
    student_notes: str = Form(""),
    user: dict = Depends(require_siswa)
):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        quiz = cursor.fetchone()
        if not quiz or quiz["quiz_type"] != "ujian":
            raise HTTPException(status_code=400, detail="Pengajuan perbaikan hanya untuk Ujian Sumatif.")

        cursor.execute("SELECT * FROM quiz_attempts WHERE user_id = ? AND quiz_id = ? ORDER BY id DESC LIMIT 1", (user["id"], quiz_id))
        last_attempt = cursor.fetchone()
        if not last_attempt:
            return RedirectResponse(url=f"/siswa/kuis/{quiz_id}/hasil?err=Anda+belum+memiliki+riwayat+pengerjaan+ujian.", status_code=status.HTTP_302_FOUND)

        if last_attempt["score"] > 75:
            return RedirectResponse(url=f"/siswa/kuis/{quiz_id}/hasil?msg=Nilai+Anda+sudah+memenuhi+KKM+(Lulus),+tidak+memerlukan+perbaikan.", status_code=status.HTTP_302_FOUND)

        # Cek apakah sudah ada request pending / approved
        cursor.execute("SELECT * FROM quiz_remedial_requests WHERE user_id = ? AND quiz_id = ? AND status IN ('pending', 'approved')", (user["id"], quiz_id))
        existing = cursor.fetchone()
        if existing:
            return RedirectResponse(url=f"/siswa/kuis/{quiz_id}/hasil?msg=Permohonan+perbaikan+sudah+diajukan+sebelumnya.", status_code=status.HTTP_302_FOUND)

        cursor.execute("""
            INSERT INTO quiz_remedial_requests (user_id, quiz_id, attempt_id, score, status, student_notes)
            VALUES (?, ?, ?, ?, 'pending', ?)
        """, (user["id"], quiz_id, last_attempt["id"], last_attempt["score"], student_notes))

        log_activity(user["id"], "AJUKAN_REMEDIAL", f"Siswa mengajukan remedial ujian '{quiz['title']}' dengan skor {last_attempt['score']}", conn=conn)

    return RedirectResponse(url=f"/siswa/kuis/{quiz_id}/hasil?msg=Permohonan+perbaikan+berhasil+dikirimkan+ke+Guru.+Menunggu+persetujuan.", status_code=status.HTTP_302_FOUND)

# ==========================================
# SISWA: JURNAL REFLEKSI (SURVEY SKALA & PESAN)
# ==========================================
@router.get("/refleksi", response_class=HTMLResponse)
def jurnal_refleksi_page(request: Request, user: dict = Depends(require_siswa), msg: str = None, err: str = None):
    with db_session() as conn:
        cursor = conn.cursor()
        progression = get_student_progression(user["id"], conn)
        if not progression["eval"]["unlocked"]:
            return RedirectResponse(
                url="/siswa?err=Jurnal+Refleksi+baru+bisa+diisi+setelah+kamu+menyelesaikan+rangkaian+Pertemuan+1,+2,+dan+3.",
                status_code=status.HTTP_302_FOUND
            )

        cursor.execute("SELECT * FROM reflections WHERE user_id = ? ORDER BY submitted_at DESC", (user["id"],))
        reflections = [dict(r) for r in cursor.fetchall()]

    return templates.TemplateResponse(request=request, name="siswa/refleksi.html", context={
        "user": user,
        "active_nav": "refleksi",
        "reflections": reflections,
        "msg": msg,
        "err": err
    })

@router.post("/refleksi/submit")
def submit_refleksi(
    rating_decomposition: int = Form(5),
    rating_pattern: int = Form(5),
    rating_abstraction: int = Form(5),
    rating_algorithm: int = Form(5),
    rating_dryrun: int = Form(5),
    rating_experience: int = Form(5),
    impression: str = Form(""),
    message: str = Form(""),
    q1_difficult: str = Form(""),
    q2_strategy: str = Form(""),
    q3_different: str = Form(""),
    q4_realworld: str = Form(""),
    user: dict = Depends(require_siswa)
):
    with db_session() as conn:
        cursor = conn.cursor()
        
        # Jika pertanyaan esai lama kosong, isi dari impression dan message agar konsisten
        q1 = q1_difficult if q1_difficult else impression
        q2 = q2_strategy if q2_strategy else message
        q3 = q3_different if q3_different else "-"
        q4 = q4_realworld if q4_realworld else "-"

        cursor.execute("""
            INSERT INTO reflections (
                unit_id, meeting_number, user_id,
                q1_difficult, q2_strategy, q3_different, q4_realworld,
                rating_decomposition, rating_pattern, rating_abstraction,
                rating_algorithm, rating_dryrun, rating_experience,
                impression, message
            )
            VALUES (1, 3, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user["id"],
            q1, q2, q3, q4,
            rating_decomposition, rating_pattern, rating_abstraction,
            rating_algorithm, rating_dryrun, rating_experience,
            impression, message
        ))

        log_activity(user["id"], "ISI_REFLEKSI", "Siswa mengisi survey jurnal refleksi pembelajaran Unit 1", conn=conn)

    return RedirectResponse(url="/siswa/refleksi?msg=Terima+kasih!+Survey+refleksi+pembelajaran+berhasil+disimpan.+Seluruh+rangkaian+Unit+1+tuntas!", status_code=status.HTTP_302_FOUND)
