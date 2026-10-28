import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any
from app.config import DB_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 30000;")
    return conn

@contextmanager
def db_session() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def log_activity(user_id: int, action: str, details: str = "", ip_address: str = "127.0.0.1", conn: Optional[sqlite3.Connection] = None):
    query = """
        INSERT INTO activity_logs (user_id, action, details, ip_address)
        VALUES (?, ?, ?, ?)
    """
    try:
        if conn:
            conn.execute(query, (user_id, action, details, ip_address))
        else:
            with db_session() as new_conn:
                new_conn.execute(query, (user_id, action, details, ip_address))
    except Exception as e:
        print(f"[LOG ERROR] {e}")

def init_tables():
    with db_session() as conn:
        cursor = conn.cursor()
        
        # 1. Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('guru', 'siswa')),
            class_name TEXT DEFAULT 'X-1',
            must_change_password INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Migration: ensure must_change_password exists in users
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN must_change_password INTEGER DEFAULT 0;")
        except Exception:
            pass

        # 2. Activity Logs Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT DEFAULT '',
            ip_address TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 3. Password Reset Requests Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            full_name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            reason TEXT DEFAULT 'Lupa kata sandi',
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'completed')),
            temp_password TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP DEFAULT NULL,
            approved_by INTEGER DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 4. Units Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_number INTEGER UNIQUE NOT NULL,
            title TEXT NOT NULL,
            element TEXT NOT NULL DEFAULT 'Berpikir Komputasional',
            description TEXT NOT NULL,
            objective TEXT NOT NULL,
            status TEXT DEFAULT 'published' CHECK(status IN ('draft', 'published')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 5. Lessons Table (Pertemuan)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_id INTEGER NOT NULL,
            meeting_number INTEGER NOT NULL,
            title TEXT NOT NULL,
            tp_focus TEXT NOT NULL,
            duration TEXT DEFAULT '2 JP (90 Menit)',
            principles TEXT DEFAULT 'Berkesadaran, Bermakna, Menggembirakan',
            narrative_title TEXT DEFAULT '',
            narrative_content TEXT DEFAULT '',
            content_html TEXT NOT NULL,
            interactive_type TEXT DEFAULT 'none',
            slide_file_path TEXT DEFAULT '',
            slide_file_name TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
        );
        """)

        # 6. Lesson Progress Table (Prasyarat Progres Alur Pembelajaran Siswa)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lesson_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            meeting_number INTEGER NOT NULL,
            material_read INTEGER DEFAULT 0,
            slide_accessed INTEGER DEFAULT 0,
            sim_completed INTEGER DEFAULT 0,
            assignment_submitted INTEGER DEFAULT 0,
            quiz_completed INTEGER DEFAULT 0,
            is_completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, meeting_number)
        );
        """)

        # 7. Assignments Table (Tugas & LKPD)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_id INTEGER NOT NULL,
            meeting_number INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            assignment_type TEXT DEFAULT 'LKPD' CHECK(assignment_type IN ('LKPD', 'Tugas', 'Projek')),
            max_score INTEGER DEFAULT 100,
            due_date TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
        );
        """)

        # 8. Submissions Table (Pengumpulan Tugas)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            group_members TEXT DEFAULT '',
            submission_text TEXT DEFAULT '',
            file_path TEXT DEFAULT '',
            score INTEGER DEFAULT NULL,
            feedback TEXT DEFAULT '',
            status TEXT DEFAULT 'submitted' CHECK(status IN ('submitted', 'graded', 'revision')),
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            graded_at TIMESTAMP DEFAULT NULL,
            FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 9. Quizzes Table (Kuis, Latihan & Ujian)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_id INTEGER NOT NULL,
            meeting_number INTEGER DEFAULT 1,
            title TEXT NOT NULL,
            quiz_type TEXT DEFAULT 'latihan' CHECK(quiz_type IN ('latihan', 'kuis', 'ujian')),
            duration_minutes INTEGER DEFAULT 15,
            pass_score INTEGER DEFAULT 75,
            status TEXT DEFAULT 'published' CHECK(status IN ('draft', 'published')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
        );
        """)

        # 10. Quiz Questions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            option_e TEXT DEFAULT '',
            correct_option TEXT NOT NULL CHECK(correct_option IN ('A', 'B', 'C', 'D', 'E')),
            explanation TEXT DEFAULT '',
            order_num INTEGER DEFAULT 1,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
        );
        """)

        # 11. Quiz Attempts Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            answers_json TEXT DEFAULT '{}',
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 11b. Quiz Remedial Requests Table (Permohonan Perbaikan Ujian)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_remedial_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            attempt_id INTEGER DEFAULT NULL,
            score INTEGER NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
            student_notes TEXT DEFAULT '',
            teacher_notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP DEFAULT NULL,
            reviewed_by INTEGER DEFAULT NULL,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
        );
        """)

        # 12. Reflections Table (Jurnal Refleksi & Tiket Keluar)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_id INTEGER NOT NULL,
            meeting_number INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            q1_difficult TEXT NOT NULL,
            q2_strategy TEXT NOT NULL,
            q3_different TEXT NOT NULL,
            q4_realworld TEXT NOT NULL,
            rating_decomposition INTEGER DEFAULT 5,
            rating_pattern INTEGER DEFAULT 5,
            rating_abstraction INTEGER DEFAULT 5,
            rating_algorithm INTEGER DEFAULT 5,
            rating_dryrun INTEGER DEFAULT 5,
            rating_experience INTEGER DEFAULT 5,
            impression TEXT DEFAULT '',
            message TEXT DEFAULT '',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 13. Interactive Progress Table (State simulasi & lab)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactive_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            unit_id INTEGER NOT NULL,
            activity_key TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            state_data TEXT DEFAULT '{}',
            completed INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, unit_id, activity_key)
        );
        """)
        print("[DB] Database tables successfully created/migrated with WAL mode enabled!")

# ==========================================
# PROGRESS & PRASYARAT PEMBELAJARAN SISWA
# ==========================================
def get_student_progression(user_id: int, conn: sqlite3.Connection) -> Dict[str, Any]:
    """
    Menghitung status checklist rangkaian aktivitas untuk setiap pertemuan.
    Rangkaian tiap pertemuan:
    1. Mengakses materi & slide presentasi
    2. Mengakses & menyelesaikan Lab Simulasi
    3. Mengerjakan & mengumpulkan LKPD
    4. Mengerjakan kuis unit (untuk Pertemuan 1)
    """
    # Pertemuan 1
    p1_read = conn.execute("""
        SELECT COUNT(*) as c FROM activity_logs 
        WHERE user_id = ? AND action IN ('BACA_MODUL', 'BACA_SLIDE') AND (details LIKE '%Pertemuan 1%' OR details LIKE '%Dekomposisi%')
    """, (user_id,)).fetchone()["c"] > 0

    p1_slide = conn.execute("""
        SELECT COUNT(*) as c FROM activity_logs 
        WHERE user_id = ? AND action = 'BACA_SLIDE' AND (details LIKE '%Pertemuan 1%' OR details LIKE '%Dekomposisi%')
    """, (user_id,)).fetchone()["c"] > 0
    p1_slide_done = p1_slide or False

    p1_sim = conn.execute("""
        SELECT COUNT(*) as c FROM interactive_progress 
        WHERE user_id = ? AND activity_key = 'pohon_dekomposisi' AND completed = 1
    """, (user_id,)).fetchone()["c"] > 0 or conn.execute("""
        SELECT COUNT(*) as c FROM activity_logs 
        WHERE user_id = ? AND action = 'LAB_SIMULASI' AND (details LIKE '%Pohon Dekomposisi%' OR details LIKE '%pohon_dekomposisi%')
    """, (user_id,)).fetchone()["c"] > 0

    p1_lkpd = conn.execute("""
        SELECT COUNT(*) as c FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.user_id = ? AND a.meeting_number = 1
    """, (user_id,)).fetchone()["c"] > 0

    p1_quiz = conn.execute("""
        SELECT COUNT(*) as c FROM quiz_attempts qa
        JOIN quizzes q ON qa.quiz_id = q.id
        WHERE qa.user_id = ? AND q.meeting_number = 1
    """, (user_id,)).fetchone()["c"] > 0
    p1_quiz_score = conn.execute("""
        SELECT score FROM quiz_attempts qa
        JOIN quizzes q ON qa.quiz_id = q.id
        WHERE qa.user_id = ? AND q.meeting_number = 1
        ORDER BY qa.completed_at DESC LIMIT 1
    """, (user_id,)).fetchone()
    p1_score_val = p1_quiz_score["score"] if p1_quiz_score else None

    p1_completed = p1_read and p1_slide_done and p1_sim and p1_lkpd and p1_quiz

    # Pertemuan 2 (Terbuka HANYA JIKA Pertemuan 1 Selesai)
    p2_unlocked = p1_completed

    p2_read = conn.execute("""
        SELECT COUNT(*) as c FROM activity_logs 
        WHERE user_id = ? AND action IN ('BACA_MODUL', 'BACA_SLIDE') AND (details LIKE '%Pertemuan 2%' OR details LIKE '%Abstraksi%')
    """, (user_id,)).fetchone()["c"] > 0

    p2_slide = conn.execute("""
        SELECT COUNT(*) as c FROM activity_logs 
        WHERE user_id = ? AND action = 'BACA_SLIDE' AND (details LIKE '%Pertemuan 2%' OR details LIKE '%Abstraksi%')
    """, (user_id,)).fetchone()["c"] > 0
    p2_row = conn.execute("SELECT slide_file_path FROM lessons WHERE meeting_number = 2").fetchone()
    p2_has_slide = bool(p2_row["slide_file_path"]) if p2_row else False
    p2_slide_done = p2_slide if p2_has_slide else (p2_slide or p2_read)

    p2_sim = conn.execute("""
        SELECT COUNT(*) as c FROM interactive_progress 
        WHERE user_id = ? AND activity_key = 'peta_abstraksi' AND completed = 1
    """, (user_id,)).fetchone()["c"] > 0 or conn.execute("""
        SELECT COUNT(*) as c FROM activity_logs 
        WHERE user_id = ? AND action = 'LAB_SIMULASI' AND (details LIKE '%Peta Abstraksi%' OR details LIKE '%peta_abstraksi%')
    """, (user_id,)).fetchone()["c"] > 0

    p2_lkpd = conn.execute("""
        SELECT COUNT(*) as c FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.user_id = ? AND a.meeting_number = 2
    """, (user_id,)).fetchone()["c"] > 0

    p2_completed = p2_unlocked and p2_read and p2_slide_done and p2_sim and p2_lkpd

    # Pertemuan 3 (Terbuka HANYA JIKA Pertemuan 2 Selesai)
    p3_unlocked = p2_completed

    p3_read = conn.execute("""
        SELECT COUNT(*) as c FROM activity_logs 
        WHERE user_id = ? AND action IN ('BACA_MODUL', 'BACA_SLIDE') AND (details LIKE '%Pertemuan 3%' OR details LIKE '%Algoritma%')
    """, (user_id,)).fetchone()["c"] > 0

    p3_slide = conn.execute("""
        SELECT COUNT(*) as c FROM activity_logs 
        WHERE user_id = ? AND action = 'BACA_SLIDE' AND (details LIKE '%Pertemuan 3%' OR details LIKE '%Algoritma%')
    """, (user_id,)).fetchone()["c"] > 0
    p3_row = conn.execute("SELECT slide_file_path FROM lessons WHERE meeting_number = 3").fetchone()
    p3_has_slide = bool(p3_row["slide_file_path"]) if p3_row else False
    p3_slide_done = p3_slide if p3_has_slide else (p3_slide or p3_read)

    p3_sim = conn.execute("""
        SELECT COUNT(*) as c FROM interactive_progress 
        WHERE user_id = ? AND activity_key = 'dry_run_simulator' AND completed = 1
    """, (user_id,)).fetchone()["c"] > 0 or conn.execute("""
        SELECT COUNT(*) as c FROM activity_logs 
        WHERE user_id = ? AND action = 'LAB_SIMULASI' AND (details LIKE '%Dry-Run%' OR details LIKE '%dry_run%')
    """, (user_id,)).fetchone()["c"] > 0

    p3_lkpd = conn.execute("""
        SELECT COUNT(*) as c FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.user_id = ? AND a.meeting_number = 3
    """, (user_id,)).fetchone()["c"] > 0

    p3_completed = p3_unlocked and p3_read and p3_slide_done and p3_sim and p3_lkpd

    # Evaluasi Akhir (Ujian Sumatif & Refleksi) (Terbuka HANYA JIKA Pertemuan 3 Selesai)
    exam_unlocked = p3_completed

    exam_taken = conn.execute("""
        SELECT COUNT(*) as c FROM quiz_attempts qa
        JOIN quizzes q ON qa.quiz_id = q.id
        WHERE qa.user_id = ? AND q.quiz_type = 'ujian'
    """, (user_id,)).fetchone()["c"] > 0
    exam_score_row = conn.execute("""
        SELECT score FROM quiz_attempts qa
        JOIN quizzes q ON qa.quiz_id = q.id
        WHERE qa.user_id = ? AND q.quiz_type = 'ujian'
        ORDER BY qa.completed_at DESC LIMIT 1
    """, (user_id,)).fetchone()
    exam_score_val = exam_score_row["score"] if exam_score_row else None

    reflection_taken = conn.execute("""
        SELECT COUNT(*) as c FROM reflections WHERE user_id = ?
    """, (user_id,)).fetchone()["c"] > 0

    # Total checklist score for overall progress
    total_items = 13
    done_items = sum([
        1 if p1_read else 0,
        1 if p1_slide_done else 0,
        1 if p1_sim else 0,
        1 if p1_lkpd else 0,
        1 if p1_quiz else 0,
        1 if p2_read else 0,
        1 if p2_slide_done else 0,
        1 if p2_sim else 0,
        1 if p2_lkpd else 0,
        1 if p3_read else 0,
        1 if p3_slide_done else 0,
        1 if p3_sim else 0,
        1 if p3_lkpd else 0
    ])
    if exam_taken: done_items += 1
    if reflection_taken: done_items += 1
    progress_percentage = min(100, int((done_items / 15) * 100))

    return {
        "p1": {
            "unlocked": True,
            "completed": p1_completed,
            "read": p1_read,
            "slide": p1_slide_done,
            "sim": p1_sim,
            "lkpd": p1_lkpd,
            "quiz": p1_quiz,
            "quiz_score": p1_score_val
        },
        "p2": {
            "unlocked": p2_unlocked,
            "completed": p2_completed,
            "read": p2_read,
            "slide": p2_slide_done,
            "sim": p2_sim,
            "lkpd": p2_lkpd,
            "lock_reason": "Selesaikan seluruh rangkaian aktivitas Pertemuan 1 terlebih dahulu."
        },
        "p3": {
            "unlocked": p3_unlocked,
            "completed": p3_completed,
            "read": p3_read,
            "slide": p3_slide_done,
            "sim": p3_sim,
            "lkpd": p3_lkpd,
            "lock_reason": "Selesaikan seluruh rangkaian aktivitas Pertemuan 2 terlebih dahulu."
        },
        "eval": {
            "unlocked": exam_unlocked,
            "exam_taken": exam_taken,
            "exam_score": exam_score_val,
            "reflection_taken": reflection_taken,
            "lock_reason": "Selesaikan seluruh rangkaian materi Pertemuan 1, 2, dan 3 terlebih dahulu."
        },
        "overall_percentage": progress_percentage
    }
