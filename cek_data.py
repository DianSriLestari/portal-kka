import sqlite3
import os
import sys

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'kka_learning.db')

if not os.path.exists(DB_PATH):
    print(f"[ERROR] File database tidak ditemukan di: {DB_PATH}")
    sys.exit(1)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 75)
print("       RINGKASAN DATA MASUK - PORTAL PEMBELAJARAN KKA FASE E")
print("=" * 75)

# 1. Statistik Pengguna
total_siswa = cursor.execute("SELECT COUNT(*) as c FROM users WHERE role='siswa'").fetchone()["c"]
total_guru = cursor.execute("SELECT COUNT(*) as c FROM users WHERE role='guru'").fetchone()["c"]
print(f"👥 Pengguna Terdaftar: {total_siswa} Siswa | {total_guru} Guru")

# 2. Pengumpulan LKPD Terbaru
print("\n📝 5 PENGUMPULAN TUGAS / LKPD TERAKHIR:")
print("-" * 75)
submissions = cursor.execute("""
    SELECT s.*, u.full_name, u.class_name, a.title as tugas_title, a.meeting_number
    FROM submissions s
    JOIN users u ON s.user_id = u.id
    JOIN assignments a ON s.assignment_id = a.id
    ORDER BY s.submitted_at DESC LIMIT 5
""").fetchall()

if submissions:
    for s in submissions:
        score_badge = f"[Nilai: {s['score']}]" if s['score'] is not None else "[Belum Dinilai]"
        print(f"• {s['submitted_at'][:16]} | {s['full_name']} ({s['class_name']})")
        print(f"  -> {s['tugas_title']} (Pertemuan {s['meeting_number']}) {score_badge}")
        if s['submission_text']:
            snippet = s['submission_text'].replace('\n', ' ')[:70]
            print(f"  -> Jawaban: \"{snippet}...\"")
else:
    print("  (Belum ada pengumpulan tugas)")

# 3. Pengerjaan Kuis & Ujian Terbaru
print("\n🎯 5 PENGERJAAN KUIS / UJIAN SUMATIF TERAKHIR:")
print("-" * 75)
attempts = cursor.execute("""
    SELECT qa.*, u.full_name, u.class_name, q.title as quiz_title, q.quiz_type, q.pass_score
    FROM quiz_attempts qa
    JOIN users u ON qa.user_id = u.id
    JOIN quizzes q ON qa.quiz_id = q.id
    ORDER BY qa.completed_at DESC LIMIT 5
""").fetchall()

if attempts:
    for a in attempts:
        status_kkm = "LULUS" if a['score'] > 75 else "BELUM TUNTAS"
        print(f"• {a['completed_at'][:16]} | {a['full_name']} ({a['class_name']})")
        print(f"  -> {a['quiz_title']} | Skor: {a['score']}/100 [{status_kkm}] (Benar: {a['correct_answers']}/{a['total_questions']})")
else:
    print("  (Belum ada pengerjaan kuis)")

# 4. Permohonan Remedial Siswa
print("\n📢 PERMOHONAN REMEDIAL UJIAN SISWA:")
print("-" * 75)
remedials = cursor.execute("""
    SELECT r.*, u.full_name, u.class_name, q.title as quiz_title
    FROM quiz_remedial_requests r
    JOIN users u ON r.user_id = u.id
    JOIN quizzes q ON r.quiz_id = q.id
    ORDER BY r.created_at DESC LIMIT 5
""").fetchall()

if remedials:
    for r in remedials:
        status_tag = f"[{r['status'].upper()}]"
        print(f"• {r['created_at'][:16]} | {status_tag} {r['full_name']} ({r['class_name']})")
        print(f"  -> {r['quiz_title']} | Skor Awal: {r['score']} | Catatan: \"{r['student_notes'] or '-'}\"")
else:
    print("  (Tidak ada permohonan remedial pending)")

# 5. Jurnal Refleksi Siswa Terbaru
print("\n✨ 5 JURNAL REFLEKSI TERAKHIR DARI SISWA:")
print("-" * 75)
reflections = cursor.execute("""
    SELECT r.*, u.full_name, u.class_name
    FROM reflections r
    JOIN users u ON r.user_id = u.id
    ORDER BY r.submitted_at DESC LIMIT 5
""").fetchall()

if reflections:
    for ref in reflections:
        ratings_str = f"Dekomposisi: {ref['rating_decomposition']}/5, Algoritma: {ref['rating_algorithm']}/5" if ref['rating_decomposition'] else ""
        print(f"• {ref['submitted_at'][:16]} | {ref['full_name']} ({ref['class_name']}) {ratings_str}")
        kesan = ref['impression'] or ref['q1_difficult'] or '-'
        pesan = ref['message'] or ref['q2_strategy'] or '-'
        print(f"  -> Kesan: \"{kesan[:65]}...\"")
        print(f"  -> Pesan: \"{pesan[:65]}...\"")
else:
    print("  (Belum ada jurnal refleksi yang masuk)")

print("\n" + "=" * 75)
print("💡 TIPS: Anda juga dapat melihat laporan lengkap secara visual dan mengunduh")
print("   file Excel/CSV di menu Guru: /guru/laporan")
print("=" * 75)

conn.close()
