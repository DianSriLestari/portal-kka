import json
from app.database import db_session, init_tables
from app.auth import hash_password

def seed_database():
    init_tables()
    
    with db_session() as conn:
        cursor = conn.cursor()

        # ==========================================
        # 1. SEED AKUN GURU & SISWA
        # ==========================================
        users_to_seed = [
            # Akun Guru 1
            ("guru", "guru123", "Suharno, S.Kom.", "guru", "Guru KKA"),
            # Akun Guru 2 (Permintaan khusus user: guruSH / guru123)
            ("guruSH", "guru123", "Suharno, S.Kom. (Pengampu KKA)", "guru", "Guru KKA"),
            # Akun Siswa Kelas X
            ("siswa1", "siswa123", "Ahmad Rizki Pratama", "siswa", "X-1"),
            ("siswa2", "siswa123", "Dewi Lestari", "siswa", "X-1"),
            ("siswa3", "siswa123", "Farhan Maulana", "siswa", "X-1"),
            ("siswa4", "siswa123", "Nabila Putri Maharani", "siswa", "X-1"),
            ("siswa5", "siswa123", "Rian Hidayat", "siswa", "X-1"),
        ]

        for username, plain_pass, full_name, role, class_name in users_to_seed:
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if not cursor.fetchone():
                pw_hash, salt = hash_password(plain_pass)
                cursor.execute("""
                    INSERT INTO users (username, password_hash, salt, full_name, role, class_name)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, pw_hash, salt, full_name, role, class_name))
                print(f"[USER] Akun dibuat: {username} ({role})")

        # ==========================================
        # 2. SEED UNIT 1 (BERPIKIR KOMPUTASIONAL)
        # ==========================================
        cursor.execute("SELECT id FROM units WHERE unit_number = 1")
        unit_row = cursor.fetchone()
        if not unit_row:
            cursor.execute("""
                INSERT INTO units (unit_number, title, element, description, objective, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                1,
                "Pemecahan Masalah Kompleks Sehari-hari",
                "Berpikir Komputasional",
                "Mempelajari cara menyelesaikan masalah autentik lingkungan sekolah (antrean kantin, sampah, piket) menggunakan 4 pilar berpikir komputasional.",
                "Pada akhir unit ini, murid mampu mengidentifikasi masalah kompleks, menguraikannya (dekomposisi), menemukan pola, menyaring informasi (abstraksi), serta merancang dan menguji solusi (algoritma & dry run).",
                "published"
            ))
            unit_id = cursor.lastrowid
            print(f"[UNIT] Unit 1 berhasil dibuat (ID: {unit_id})")
        else:
            unit_id = unit_row["id"]

        # ==========================================
        # 3. SEED PERTEMUAN (LESSONS) UNIT 1
        # ==========================================
        cursor.execute("SELECT COUNT(*) as cnt FROM lessons WHERE unit_id = ?", (unit_id,))
        if cursor.fetchone()["cnt"] == 0:
            lessons_data = [
                (
                    unit_id,
                    1,
                    "Pertemuan 1: Memahami Masalah Kompleks & Dekomposisi",
                    "TP 1: Mengidentifikasi permasalahan kompleks di lingkungan sehari-hari dan menguraikannya menjadi sub-masalah yang lebih sederhana.",
                    "2 JP (90 Menit)",
                    "Berkesadaran (Menyadari proses berpikir), Bermakna (Konteks kantin sekolah), Menggembirakan (Permainan Dekomposisi)",
                    "Studi Kasus: Dari Kantin yang Penuh ke Solusi Terstruktur (Bagian 1)",
                    "Rani dan Dimas adalah pengurus OSIS SMAN 7 Pontianak. Setiap jam istirahat, kantin sekolah penuh sesak dan banyak siswa kehabisan waktu sebelum bel masuk. Dimas langsung mengusulkan 'Tambah saja penjualnya!', namun Rani mengajak berpikir terstruktur: 'Kita belum tahu akar masalahnya. Mari kita bedah dulu masalahnya.'",
                    """
                    <div class="prose max-w-none">
                        <h3 class="text-xl font-bold text-indigo-900">Apa itu Masalah Kompleks?</h3>
                        <p>Masalah kompleks adalah masalah yang memiliki banyak faktor yang saling berkaitan dan umumnya memiliki beberapa alternatif solusi. Contohnya: antrean kantin saat jam istirahat, penumpukan sampah di sekolah, dan jadwal piket yang tidak efektif.</p>
                        
                        <h3 class="text-xl font-bold text-indigo-900 mt-6">Pilar 1: Dekomposisi</h3>
                        <p><strong>Dekomposisi</strong> adalah teknik memecah masalah besar menjadi sub-masalah yang lebih kecil dan dapat dikelola secara mandiri.</p>
                        <div class="bg-amber-50 border-l-4 border-amber-500 p-4 my-4">
                            <p class="font-semibold text-amber-800">Prinsip Penting:</p>
                            <p class="text-amber-700">Dekomposisi adalah <em>membagi masalahnya</em>, bukan membagi orangnya. Pembagian tugas kepada teman kelompok dilakukan setelah pohon sub-masalah tersusun dengan jelas!</p>
                        </div>

                        <h4 class="font-bold text-gray-800">Langkah Membuat Pohon Dekomposisi:</h4>
                        <ol class="list-decimal pl-5 space-y-2">
                            <li>Rumuskan masalah utama menggunakan prinsip <strong>5W1H</strong>.</li>
                            <li>Pecah menjadi tingkat 1 (aspek-aspek besar, misal: kedatangan siswa, layanan kasir, penataan jalur).</li>
                            <li>Pecah kembali ke tingkat 2 sampai dapat dikerjakan oleh 1 orang atau dalam 1 langkah kerja.</li>
                        </ol>
                    </div>
                    """,
                    "pohon_dekomposisi"
                ),
                (
                    unit_id,
                    2,
                    "Pertemuan 2: Menemukan Pola & Abstraksi Data",
                    "TP 2: Menemukan pola dan menyederhanakan masalah melalui abstraksi untuk menentukan data penting serta alternatif solusi.",
                    "2 JP (90 Menit)",
                    "Bermakna (Mengolah data nyata), Menggembirakan (Simulasi sortir kartu informasi)",
                    "Studi Kasus: Rani & Dimas Menganalisis Data Antrean (Bagian 2)",
                    "Selama 3 hari, Rani dan Dimas mencatat kedatangan murid tiap 5 menit tanpa mencatat identitas pribadi siapa pun demi privasi. Mereka menemukan pola mengejutkan: antrean selalu melonjak drastis hanya di 5 menit pertama, lalu berangsur turun. Maka fokus solusi adalah menangani 5 menit krusial tersebut!",
                    """
                    <div class="prose max-w-none">
                        <h3 class="text-xl font-bold text-indigo-900">Pilar 2: Pengenalan Pola</h3>
                        <p>Pengenalan pola adalah kemampuan melihat kesamaan, keteraturan, atau tren berulang pada data atau situasi. Menemukan pola membantu kita menduga penyebab utama masalah.</p>
                        
                        <div class="overflow-x-auto my-4">
                            <table class="min-w-full bg-white border border-gray-200 text-sm">
                                <thead class="bg-indigo-50">
                                    <tr>
                                        <th class="py-2 px-4 border">Menit ke- (Waktu Istirahat)</th>
                                        <th class="py-2 px-4 border">Jumlah Siswa Mengantre</th>
                                        <th class="py-2 px-4 border">Analisis Pola</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr><td class="py-2 px-4 border text-center">0 – 5</td><td class="py-2 px-4 border text-center font-bold text-red-600">40 Siswa</td><td class="py-2 px-4 border">Puncak lonjakan (Peak hours)</td></tr>
                                    <tr><td class="py-2 px-4 border text-center">5 – 10</td><td class="py-2 px-4 border text-center font-bold text-amber-600">25 Siswa</td><td class="py-2 px-4 border">Mulai terurai</td></tr>
                                    <tr><td class="py-2 px-4 border text-center">10 – 15</td><td class="py-2 px-4 border text-center">8 Siswa</td><td class="py-2 px-4 border">Layanan normal</td></tr>
                                    <tr><td class="py-2 px-4 border text-center">15 – 20</td><td class="py-2 px-4 border text-center">2 Siswa</td><td class="py-2 px-4 border">Sepi</td></tr>
                                </tbody>
                            </table>
                        </div>

                        <h3 class="text-xl font-bold text-indigo-900 mt-6">Pilar 3: Abstraksi</h3>
                        <p><strong>Abstraksi</strong> adalah menyaring informasi: mempertahankan faktor yang memengaruhi solusi, dan mengabaikan detail yang tidak relevan.</p>
                        <p class="text-gray-700 italic">Pertanyaan kunci: "Jika informasi ini dihapus, apakah keputusan atau solusi kita berubah?"</p>
                    </div>
                    """,
                    "peta_abstraksi"
                ),
                (
                    unit_id,
                    3,
                    "Pertemuan 3: Merancang Algoritma & Uji Telusur (Dry Run)",
                    "TP 3: Merancang dan mengevaluasi solusi terstruktur berupa algoritma (flowchart/pseudocode) dan melakukan uji telusur.",
                    "2 JP (90 Menit)",
                    "Berkesadaran (Refleksi metakognisi), Menggembirakan (Uji simulator interaktif)",
                    "Studi Kasus: Menguji Logika di Atas Kertas (Bagian 3)",
                    "Rani dan Dimas menyusun aturan: 'Jika kasir 1 antreannya lebih sedikit atau sama, arahkan ke kasir 1; jika tidak ke kasir 2'. Saat diuji telusur di atas kertas (dry run), Dimas bertanya: 'Bagaimana kalau kasir 1 sedang istirahat atau tutup?'. Algoritma pun diperbaiki untuk menangani kasus khusus (edge case) tersebut!",
                    """
                    <div class="prose max-w-none">
                        <h3 class="text-xl font-bold text-indigo-900">Pilar 4: Algoritma</h3>
                        <p>Algoritma adalah urutan langkah logis, berhingga, dan tidak ambigu untuk menyelesaikan suatu masalah.</p>
                        
                        <h4 class="font-bold text-gray-800 mt-4">Ciri Algoritma yang Baik:</h4>
                        <ul class="list-disc pl-5 space-y-1">
                            <li><strong>Masukan (Input) & Keluaran (Output):</strong> Jelas data awalnya dan hasilnya.</li>
                            <li><strong>Pasti (Definiteness):</strong> Setiap instruksi jelas dan tidak multitafsir.</li>
                            <li><strong>Berhingga (Finiteness):</strong> Ada titik mulai (Mulai) dan titik akhir (Selesai).</li>
                            <li><strong>Menangani Kasus Khusus (Edge Cases):</strong> Tidak error ketika kondisi luar biasa terjadi.</li>
                        </ul>

                        <h3 class="text-xl font-bold text-indigo-900 mt-6">Uji Telusur (Dry Run)</h3>
                        <p>Uji telusur adalah teknik menguji algoritma di atas kertas atau simulator dengan berbagai skenario data uji sebelum diterapkan secara nyata.</p>
                    </div>
                    """,
                    "dry_run_simulator"
                )
            ]

            for l in lessons_data:
                cursor.execute("""
                    INSERT INTO lessons (unit_id, meeting_number, title, tp_focus, duration, principles, narrative_title, narrative_content, content_html, interactive_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, l)
            print("[LESSON] 3 Pertemuan materi Unit 1 berhasil ditambahkan.")

        # ==========================================
        # 4. SEED TUGAS & LKPD
        # ==========================================
        cursor.execute("SELECT COUNT(*) as cnt FROM assignments WHERE unit_id = ?", (unit_id,))
        if cursor.fetchone()["cnt"] == 0:
            assignments_data = [
                (
                    unit_id,
                    1,
                    "LKPD 1: Dekomposisi Masalah Kompleks Sekolah",
                    "Pilihlah salah satu masalah (Antrean Kantin, Sampah, atau Piket). Tuliskan rumusan 5W1H dan susunlah pohon dekomposisi minimal 3 tingkat lengkap dengan alasan penentuan prioritas sub-masalah.",
                    "LKPD",
                    100,
                    "Pertemuan 1"
                ),
                (
                    unit_id,
                    2,
                    "LKPD 2: Pengenalan Pola & Abstraksi Data",
                    "Catat data pengamatan, temukan minimal 2 pola data, sortir data penting vs data yang diabaikan pada tabel abstraksi, serta ajukan 2 alternatif solusi terukur.",
                    "LKPD",
                    100,
                    "Pertemuan 2"
                ),
                (
                    unit_id,
                    3,
                    "LKPD 3: Desain Algoritma & Uji Telusur (Dry Run) - Studi Kasus Diskon Belanja",
                    "Studi Kasus Penentuan Diskon Total Belanja: Pembelanjaan > Rp 1.000.000 diskon 10% (Member +5%), pembelanjaan > Rp 500.000 diskon 5%, pembelanjaan <= Rp 500.000 diskon 0%. Kerjakan Bagian 1 (Urutan Algoritma Drag-Drop) dan Bagian 2 (Susunan Flowchart Simbol & Panah Drag-Drop), lalu lakukan eksekusi uji telusur.",
                    "LKPD",
                    100,
                    "Pertemuan 3"
                )
            ]
            for a in assignments_data:
                cursor.execute("""
                    INSERT INTO assignments (unit_id, meeting_number, title, description, assignment_type, max_score, due_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, a)
            print("[ASSIGNMENT] LKPD 1, 2, dan 3 berhasil ditambahkan.")

        # ==========================================
        # 5. SEED KUIS & SOAL EVALUASI
        # ==========================================
        cursor.execute("SELECT COUNT(*) as cnt FROM quizzes WHERE unit_id = ?", (unit_id,))
        if cursor.fetchone()["cnt"] == 0:
            # Kuis 1: Berpikir Komputasional & Dekomposisi
            cursor.execute("""
                INSERT INTO quizzes (unit_id, meeting_number, title, quiz_type, duration_minutes, pass_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (unit_id, 1, "Kuis Latihan Pertemuan 1: Dekomposisi", "kuis", 15, 75, "published"))
            quiz1_id = cursor.lastrowid

            q1_questions = [
                (
                    quiz1_id,
                    "Apa yang dimaksud dengan dekomposisi dalam berpikir komputasional?",
                    "Membagi tugas kelompok secara adil kepada setiap anggota",
                    "Memecah masalah yang kompleks menjadi sub-masalah yang lebih kecil dan terkelola",
                    "Menghapus informasi yang tidak penting dari suatu masalah",
                    "Mengubah instruksi sehari-hari menjadi bahasa pemrograman komputer",
                    "B",
                    "Dekomposisi adalah teknik memecah masalah besar menjadi sub-masalah yang lebih kecil.",
                    1
                ),
                (
                    quiz1_id,
                    "Manakah di bawah ini yang merupakan ciri utama dari masalah yang kompleks?",
                    "Hanya memiliki satu jawaban benar yang pasti dan sederhana",
                    "Dapat diselesaikan dalam satu langkah mudah tanpa penyelidikan",
                    "Memiliki banyak faktor yang saling berkaitan dan beberapa alternatif solusi",
                    "Hanya dapat diselesaikan jika menggunakan komputer super cepat",
                    "C",
                    "Masalah kompleks dipengaruhi banyak faktor dinamis dan memiliki ragam solusi.",
                    2
                ),
                (
                    quiz1_id,
                    "Pada kasus antrean kantin sekolah, langkah dekomposisi yang tepat adalah...",
                    "Langsung membeli makanan dari luar sekolah",
                    "Menyalahkan petugas kantin yang lambat melayani siswa",
                    "Membedah aspek kedatangan murid, durasi layanan kasir, dan alur jalur antrean",
                    "Meminta semua murid tidak jajan saat jam istirahat",
                    "C",
                    "Membedah faktor-faktor penyebab antrean adalah inti dari dekomposisi.",
                    3
                ),
                (
                    quiz1_id,
                    "Kapan kita sebaiknya berhenti memecah masalah pada pohon dekomposisi?",
                    "Ketika masalah sudah dipecah sebanyak 10 tingkat",
                    "Ketika sub-masalah sudah cukup kecil dan spesifik untuk ditangani satu orang/satu aksi",
                    "Ketika anggota kelompok sudah merasa lelah berdiskusi",
                    "Ketika guru menyuruh berhenti",
                    "B",
                    "Dekomposisi berhenti saat sub-masalah sudah operasional dan bisa dieksekusi langsung.",
                    4
                ),
                (
                    quiz1_id,
                    "Pernyataan yang BENAR mengenai hubungan berpikir komputasional dan pemrograman adalah...",
                    "Berpikir komputasional harus selalu dilakukan dengan menulis kode di komputer",
                    "Orang yang tidak memiliki laptop tidak bisa belajar berpikir komputasional",
                    "Berpikir komputasional adalah cara berpikir memecahkan masalah, bahkan bisa secara unplugged (tanpa komputer)",
                    "Berpikir komputasional hanya berguna untuk programmer profesional",
                    "C",
                    "Berpikir komputasional adalah metode pemecahan masalah manusia yang dapat diterapkan secara unplugged.",
                    5
                )
            ]

            for q in q1_questions:
                cursor.execute("""
                    INSERT INTO quiz_questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, order_num)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, q)

            # Kuis 2: Ujian Sumatif Unit 1 (10 Soal HOTS A-E, 10 Menit, KKM > 75)
            cursor.execute("""
                INSERT INTO quizzes (unit_id, meeting_number, title, quiz_type, duration_minutes, pass_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (unit_id, 3, "Ujian Sumatif Unit 1: Algoritma, Flowchart & Uji Telusur", "ujian", 10, 75, "published"))
            quiz2_id = cursor.lastrowid

            q2_questions = [
                (
                    quiz2_id,
                    "Seorang programmer pemula merancang flowchart sistem kasir. Saat mengevaluasi kondisi apakah pelanggan memiliki kartu anggota (is_member == 'Ya'), ia menggunakan simbol persegi panjang (Process) lalu menarik dua panah bercabang bertuliskan 'Ya' dan 'Tidak' dari kotak tersebut. Berdasarkan kaidah standar diagram alir ISO/ANSI, evaluasi mengapa perancangan ini salah dan apa dampak strukturalnya?",
                    "Perancangan benar karena simbol proses dapat memproses ekspresi logika boolean apa pun.",
                    "Salah, karena simbol proses persegi panjang hanya boleh memiliki tepat satu panah alur keluaran (single exit flow); evaluasi kondisi percabangan wajib menggunakan simbol belah ketupat (Decision).",
                    "Salah, karena simbol persegi panjang seharusnya diganti dengan jajaran genjang (Input/Output) agar pembaca diagram tahu data dibaca langsung.",
                    "Salah, karena panah 'Tidak' pada simbol proses wajib selalu berbalik arah ke Terminator awal.",
                    "Benar, asalkan teks di dalam persegi panjang menggunakan format penulisan variabel huruf kapital.",
                    "B",
                    "Simbol Proses (persegi panjang) secara standar ISO hanya memiliki 1 jalur keluar (aliran sekuensial). Untuk percabangan logika dengan dua kemungkinan (Ya/Tidak atau True/False), wajib menggunakan simbol Decision (belah ketupat) yang memiliki minimal 2 jalur keluar.",
                    1
                ),
                (
                    quiz2_id,
                    "Perhatikan aturan diskon kasir minimarket berikut:\n- Belanja > Rp1.000.000: Diskon 10%. Tambahan diskon member 5% jika memiliki kartu anggota.\n- Belanja > Rp500.000 s.d. Rp1.000.000: Diskon 5% flat (tanpa tambahan member).\n- Belanja <= Rp500.000: Diskon 0%.\nSeorang pelanggan bernama Budi berbelanja senilai Rp1.200.000 dan memiliki kartu member aktif (is_member = True). Berapakah nominal uang akhir yang harus dibayarkan Budi setelah diproses oleh algoritma kasir?",
                    "Rp1.080.000",
                    "Rp1.140.000",
                    "Rp1.020.000",
                    "Rp1.050.000",
                    "Rp1.000.000",
                    "C",
                    "Total belanja Rp1.200.000 (> 1.000.000) mendapatkan diskon dasar 10%. Karena is_member bernilai True, ada tambahan diskon 5%, sehingga total diskon menjadi 15%. Nominal diskon = 15% x Rp1.200.000 = Rp180.000. Uang yang harus dibayar = Rp1.200.000 - Rp180.000 = Rp1.020.000.",
                    2
                ),
                (
                    quiz2_id,
                    "Seorang siswa menyusun diagram alir kasir dengan susunan percabangan bertingkat sebagai berikut:\n- Simbol Decision 1 mengecek: 'total_belanja > 500.000?'. Jika YA -> langsung memberi diskon 5%.\n- Cabang TIDAK dari Decision 1 baru diarahkan ke Decision 2 yang mengecek 'total_belanja > 1.000.000?'.\nAnalisislah kelemahan logika (logical bug) fatal yang terjadi pada flowchart tersebut!",
                    "Pelanggan yang belanja Rp1.500.000 hanya akan memperoleh diskon 5% karena kondisi pertama sudah terpenuhi lebih dahulu dan percabangan 1.000.000 menjadi kode tak terjangkau (unreachable code).",
                    "Pelanggan dengan total belanja Rp300.000 akan otomatis mendapatkan diskon 10% karena alur terbalik.",
                    "Program akan mengalami perulangan tak hingga (infinite loop) karena tidak menemukan terminator akhir.",
                    "Variabel total_belanja akan di-reset menjadi nol saat masuk ke percabangan kedua.",
                    "Terjadi kesalahan pembagian dengan nol (division by zero) saat menghitung persentase.",
                    "A",
                    "Dalam percabangan bersyarat bertingkat (if-else), kondisi dengan batas nilai yang lebih tinggi/spesifik (> 1.000.000) harus diperiksa terlebih dahulu sebelum kondisi yang lebih umum (> 500.000). Jika > 500.000 diperiksa lebih dulu, angka 1.500.000 sudah masuk ke cabang 5% dan kondisi 1.000.000 tidak akan pernah dieksekusi.",
                    3
                ),
                (
                    quiz2_id,
                    "Perhatikan pelacakan variabel (dry run) dari potongan algoritma antrean kantin digital berikut:\n[1] antrean = 2\n[2] total_item = 8\n[3] kasir = 'Reguler'\n[4] JIKA total_item <= 5 MAKA\n[5]     kasir = 'Express'\n[6] LAINNYA JIKA total_item <= 10 DAN antrean < 4 MAKA\n[7]     kasir = 'Semi-Express'\n[8] LAINNYA\n[9]     kasir = 'Reguler'\n[10] AKHIR JIKA\nBerdasarkan tabel penelusuran (trace table), berapakah nilai akhir dari variabel 'kasir'?",
                    "Express",
                    "Semi-Express",
                    "Reguler",
                    "Super-Express",
                    "Batal / Error",
                    "B",
                    "Baris 4 (total_item <= 5) bernilai False karena 8 > 5. Baris 6 mengecek (total_item <= 10 DAN antrean < 4) -> (8 <= 10 adalah True) DAN (2 < 4 adalah True). True AND True bernilai True, sehingga baris 7 dieksekusi dan variabel kasir bernilai 'Semi-Express'.",
                    4
                ),
                (
                    quiz2_id,
                    "Dalam perancangan flowchart transaksi pembayaran tiket bioskop online, panah dari simbol proses 'Cetak Struk Transaksi' ditarik melingkar kembali ke simbol Decision 'Apakah Kursi Masih Kosong?' tanpa adanya input pemesanan baru maupun perubahan status kuota. Dampak negatif apa yang akan dialami oleh sistem tersebut?",
                    "Sistem akan langsung berhenti secara aman (Graceful Termination).",
                    "Data kursi otomatis terduplikasi di dalam server pusat.",
                    "Sistem terjebak dalam perulangan abadi (infinite loop / deadlock) sehingga proses tidak pernah sampai ke simbol Terminator SELESAI.",
                    "Sistem secara otomatis membatalkan seluruh pembayaran pelanggan sebelumnya.",
                    "Nilai harga tiket akan dikalikan dua pada setiap putaran perulangan.",
                    "C",
                    "Algoritma wajib memiliki sifat keterbatasan (finiteness), yaitu harus berhenti setelah sejumlah langkah terhingga. Jika alur berputar kembali ke pengujian kondisi tanpa adanya perubahan variabel kontrol, sistem akan mengalami infinite loop / deadlock dan gagal mencapai titik akhir.",
                    5
                ),
                (
                    quiz2_id,
                    "Pada sistem pembayaran kasir swalayan pintar, terdapat instruksi: 'Siswa memasukkan kartu RFID atau memindai barcode belanjaan'. Simbol diagram alir standar ISO manakah yang paling tepat digunakan untuk menggambarkan instruksi tersebut beserta alasannya?",
                    "Oval (Terminator), karena merupakan batas akhir dari proses transaksi kasir.",
                    "Jajaran Genjang (Input/Output), karena sistem menerima masukan data dari entitas/perangkat luar pembaca kartu RFID.",
                    "Belah Ketupat (Decision), karena RFID dan barcode adalah dua benda fisik yang berbeda jenis.",
                    "Persegi Panjang (Process), karena RFID langsung diproses otomatis oleh memori mikroprosesor kasir.",
                    "Segilima (Off-page Connector), karena data belanjaan akan dicetak di kertas halaman lain.",
                    "B",
                    "Segala bentuk penerimaan data dari luar sistem (seperti pemindaian RFID, barcode, pembacaan sensor, pengetikan keyboard) dikategorikan sebagai operasi Input, yang dalam standar flowchart wajib menggunakan simbol jajaran genjang.",
                    6
                ),
                (
                    quiz2_id,
                    "Perhatikan tabel perbandingan hasil uji coba diskon kasir:\n- Pelanggan A (Non-Member, Belanja Rp1.200.000) -> Diskon 10%\n- Pelanggan B (Member, Belanja Rp1.200.000) -> Diskon 15%\n- Pelanggan C (Member, Belanja Rp800.000) -> Diskon 5%\n- Pelanggan D (Member, Belanja Rp350.000) -> Diskon 0%\nManakah kesimpulan analisis dekomposisi logika berikut yang PALING TEPAT mengenai pengaruh status kartu member?",
                    "Kartu member selalu memberikan diskon 5% di seluruh tingkat nominal belanja tanpa batasan.",
                    "Keuntungan tambahan diskon 5% dari status member hanya berlaku secara kondisional jika total belanja memenuhi syarat batas atas (> Rp1.000.000).",
                    "Pelanggan C mendapatkan diskon 5% semata-mata karena kartu member, bukan karena total belanjanya.",
                    "Pelanggan yang tidak memiliki kartu member tidak berhak memperoleh diskon sama sekali meskipun belanja di atas Rp1.000.000.",
                    "Pelanggan D tidak mendapat diskon karena kartu membernya mengalami kedaluwarsa sistem.",
                    "B",
                    "Analisis kasus: Pelanggan B (> 1.000.000 + member) mendapat 15% (10% + 5%). Pelanggan C (800.000) mendapat 5% murni dari tier belanja 500k-1jt, tanpa ada tambahan member. Pelanggan D (350.000) diskon 0% meski member. Jadi diskon tambahan member HANYA berlaku jika belanja > 1.000.000.",
                    7
                ),
                (
                    quiz2_id,
                    "Ketika merancang diagram alir sistem kasir yang sangat kompleks dengan banyak percabangan validasi, diagram tidak muat dalam satu halaman dan harus dilanjutkan ke lembar kertas / halaman berikutnya. Simbol standar apakah yang harus digunakan sebagai konektor antar-halaman?",
                    "Lingkaran kecil (On-page Connector)",
                    "Segilima meruncing ke bawah (Off-page Connector)",
                    "Garis panah ganda berlawanan arah",
                    "Dua belah ketupat yang berhimpitan",
                    "Persegi panjang dengan garis ganda di kedua sisinya (Predefined Process)",
                    "B",
                    "Simbol Off-page Connector (berbentuk segi lima mirip bendera meruncing ke bawah) digunakan untuk menyambungkan alur diagram alir yang berpindah ke halaman lain. Sedangkan lingkaran kecil hanya digunakan untuk penghubung di halaman yang sama (On-page).",
                    8
                ),
                (
                    quiz2_id,
                    "Seorang kasir melayani transaksi pelanggan non-member dengan total belanja tepat Rp1.000.000 (satu juta rupiah pas). Jika kondisi pada flowchart kasir dirancang dengan ekspresi perbandingan 'total_belanja > 1.000.000' (menggunakan operator lebih dari tanpa sama dengan), alur manakah yang akan dilewati sistem dan berapa diskon yang diperoleh pelanggan?",
                    "Alur 'Ya' pada kondisi 1.000.000, sehingga pelanggan mendapatkan diskon 10%.",
                    "Alur 'Tidak' pada kondisi 1.000.000, lalu masuk ke cabang 'total_belanja > 500.000' (Ya) sehingga mendapatkan diskon 5%.",
                    "Alur menghasilkan error logika 'Undefined Boundary' karena angka satu juta pas tidak terdefinisi.",
                    "Langsung melompat ke Terminator SELESAI tanpa menghitung total pembayaran.",
                    "Mendapatkan diskon 15% karena angka batas dianggap batas promosi tertinggi.",
                    "B",
                    "Uji telusur nilai batas (boundary testing): Untuk total_belanja = 1.000.000, ekspresi 1.000.000 > 1.000.000 bernilai FALSE (Tidak). Maka alur lanjut ke pengujian berikutnya: 1.000.000 > 500.000 yang bernilai TRUE (Ya), sehingga pelanggan memperoleh diskon 5%.",
                    9
                ),
                (
                    quiz2_id,
                    "Perhatikan 7 tahapan acak dalam perancangan algoritma perhitungan transaksi diskon kasir:\n[1] Masukkan total_belanja dan status is_member\n[2] Tampilkan total_bayar dan cetak struk belanja\n[3] Hitung total_bayar = total_belanja - nilai_diskon\n[4] Mulai\n[5] Tentukan persentase_diskon berdasarkan aturan percabangan belanja dan member\n[6] Selesai\n[7] Hitung nilai_diskon = (persentase_diskon / 100) * total_belanja\nUrutan algoritma yang logis, terstruktur, dan efisien dari awal hingga akhir adalah...",
                    "[4] -> [1] -> [5] -> [7] -> [3] -> [2] -> [6]",
                    "[4] -> [5] -> [1] -> [3] -> [7] -> [2] -> [6]",
                    "[1] -> [4] -> [5] -> [7] -> [3] -> [2] -> [6]",
                    "[4] -> [1] -> [3] -> [5] -> [7] -> [2] -> [6]",
                    "[4] -> [1] -> [7] -> [5] -> [3] -> [2] -> [6]",
                    "A",
                    "Urutan sekuensial logis yang benar: (4) Mulai -> (1) Masukkan data input -> (5) Evaluasi kondisi percabangan untuk persentase diskon -> (7) Hitung nominal potongan diskon -> (3) Hitung total pembayaran akhir -> (2) Tampilkan output struk -> (6) Selesai. Maka urutan yang benar adalah [4]->[1]->[5]->[7]->[3]->[2]->[6].",
                    10
                )
            ]

            for q in q2_questions:
                cursor.execute("""
                    INSERT INTO quiz_questions (quiz_id, question_text, option_a, option_b, option_c, option_d, option_e, correct_option, explanation, order_num)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, q)

            print("[QUIZ] Kuis Latihan Pertemuan 1 dan 10 Soal HOTS Ujian Sumatif Unit 1 berhasil ditambahkan.")

        print("[SUCCESS] Seeding data selesai dengan sukses!")

if __name__ == "__main__":
    seed_database()
