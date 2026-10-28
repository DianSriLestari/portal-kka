import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db_session, init_tables
from app.auth import hash_password

def run_migrations_and_seed():
    init_tables()
    
    with db_session() as conn:
        cursor = conn.cursor()
        
        # 1. Tambah guruDI jika belum ada
        cursor.execute("SELECT id FROM users WHERE username = ?", ("guruDI",))
        if not cursor.fetchone():
            pw_hash, salt = hash_password("DI2910")
            cursor.execute("""
                INSERT INTO users (username, password_hash, salt, full_name, role, class_name)
                VALUES (?, ?, ?, ?, 'guru', 'Guru KKA')
            """, ("guruDI", pw_hash, salt, "Dian Sri Lestari, S.Pd."))
            print("[OK] Akun guruDI (Dian Sri Lestari, S.Pd.) berhasil dibuat!")
        else:
            # Pastikan password dan nama sesuai jika sudah pernah dibuat
            pw_hash, salt = hash_password("DI2910")
            cursor.execute("""
                UPDATE users 
                SET password_hash = ?, salt = ?, full_name = 'Dian Sri Lestari, S.Pd.', role = 'guru'
                WHERE username = 'guruDI'
            """, (pw_hash, salt))
            print("[OK] Akun guruDI diperbarui!")

        # 2. Cek tabel password_reset_requests
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='password_reset_requests'")
        if cursor.fetchone():
            print("[OK] Tabel password_reset_requests terverifikasi!")

        # 3. Cek kolom must_change_password di users
        try:
            cursor.execute("SELECT must_change_password FROM users LIMIT 1")
            print("[OK] Kolom must_change_password di tabel users aktif!")
        except Exception as e:
            cursor.execute("ALTER TABLE users ADD COLUMN must_change_password INTEGER DEFAULT 0")
            print("[OK] Kolom must_change_password ditambahkan ke tabel users!")

        # 4. Cek kolom slide di lessons
        try:
            cursor.execute("SELECT slide_file_path FROM lessons LIMIT 1")
            print("[OK] Kolom slide_file_path di tabel lessons aktif!")
        except Exception as e:
            cursor.execute("ALTER TABLE lessons ADD COLUMN slide_file_path TEXT DEFAULT ''")
            cursor.execute("ALTER TABLE lessons ADD COLUMN slide_file_name TEXT DEFAULT ''")
            print("[OK] Kolom slide_file_path & slide_file_name ditambahkan ke lessons!")

if __name__ == "__main__":
    run_migrations_and_seed()
