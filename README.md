# Portal Pembelajaran Modul Ajar Koding dan Kecerdasan Artifisial (KKA)
### SMAN 7 Pontianak • Fase E (Kelas X)
*Dikembangkan berbasis Naskah Akademik Pembelajaran Mendalam & Dokumen Master RPP Unit 1*

---

## 🚀 Cara Menjalankan Aplikasi

### Opsi 1: Satu Klik (Windows)
Cukup klik dua kali file:
👉 **`start_app.bat`**

### Opsi 2: Menggunakan Terminal / Command Prompt
Buka PowerShell atau CMD di folder ini, lalu jalankan:
```bash
python run.py
```
Aplikasi aktif di alamat:
* **Komputer Lokal**: [http://localhost:8000](http://localhost:8000)
* **Jaringan Wi-Fi/LAN Lab Sekolah**: `http://192.168.1.88:8000` (dapat diakses bersama oleh seluruh gawai siswa di kelas).
* **Dokumentasi REST API (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔑 Akun Bawaan (Pre-seeded Credentials)

### 1. Akun Guru (Pendidik)
| Username | Password | Nama Pengajar | Peran |
|---|---|---|---|
| **`guruDI`** | `DI2910` | Dian Sri Lestari, S.Pd. | Guru Pendidik |
| **`guruSH`** | `guru123` | Suharno, S.Kom. (Pengampu KKA) | Guru Pendidik |
| **`guru`** | `guru123` | Suharno, S.Kom. | Guru Pendidik |

### 2. Akun Siswa (Kelas X-1)
| Username | Password | Nama Siswa | Kelas |
|---|---|---|---|
| **`siswa1`** | `siswa123` | Ahmad Rizki Pratama | X-1 |
| **`siswa2`** | `siswa123` | Dewi Lestari | X-1 |
| **`siswa3`** | `siswa123` | Farhan Maulana | X-1 |
| **`siswa4`** | `siswa123` | Nabila Putri Maharani | X-1 |
| **`siswa5`** | `siswa123` | Rian Hidayat | X-1 |

---

## 🌟 Fitur Baru & Perbaikan Mutakhir

### 🔐 1. Alur Lupa Password & Persetujuan Guru
* Halaman login telah dibersihkan dari teks bantuan akun default.
* Terdapat menu **"Lupa Kata Sandi?"** yang mengarahkan ke form permohonan reset password.
* Siswa mengirim permohonan reset dengan username/NISN.
* Notifikasi permohonan reset muncul di menu Guru (`/guru` dan `/guru/siswa`).
* Guru menyetujui permohonan dan sistem menerbitkan **kata sandi sementara** (misal: `KKA-XXXX`).
* Siswa mengecek status atau menerima sandi sementara, login pertama kali, dan **langsung diarahkan ke form pembuatan kata sandi baru pribadi**.

### 📊 2. Tambah Siswa via File Excel (.xlsx) & Download Template
* **Unduh Format Template**: Guru dapat mengunduh format file resmi `Format_Upload_Tambah_Siswa_KKA.xlsx` dengan header rapi (Username, Nama Lengkap, Kelas, Password).
* **Import File Excel**: Guru mengunggah file Excel berisi puluhan data siswa, sistem otomatis memvalidasi dan menyimpannya ke database.

### 📁 3. Upload File Slide Materi Pembelajaran
* Pada menu **Modul & Materi Guru (`/guru/materi`)**, tersedia tombol **"Upload File Slide"** (mendukung format `.pdf`, `.ppt`, `.pptx`).
* File slide langsung terhubung dengan pertemuan yang bersangkutan dan dapat dibuka / diunduh langsung oleh siswa di modul belajarnya.

### 👁️ 4. Perbaikan Menu Pratinjau Materi
* Menu **"Pratinjau Materi"** pada setiap pertemuan kini dapat diklik oleh Guru tanpa terlempar (*redirect*), sehingga Guru dapat meninjau langsung tampilan materi narasi Rani & Dimas, materi dekomposisi, pola, abstraksi, dan flowchart.
