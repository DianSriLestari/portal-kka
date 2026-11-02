@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Portal Pembelajaran KKA - SMAN 7 Pontianak (portalkka.my.id)

echo ============================================================
echo   PORTAL PEMBELAJARAN KKA FASE E - SMAN 7 PONTIANAK
echo   Domain Resmi: https://portalkka.my.id
echo ============================================================
echo.

:: 1. Cek & Matikan sisa proses lama jika ada yang macet
taskkill /f /im cloudflared.exe >nul 2>&1

echo [1/3] Menyalakan Server Lokal KKA...
start "Server Portal KKA (JANGAN DITUTUP)" /min python run.py

echo [2/3] Menghubungkan Tunnel Resmi ke https://portalkka.my.id ...
start "Cloudflare Tunnel (JANGAN DITUTUP)" /min "bin\cloudflared.exe" tunnel run --token eyJhIjoiMGU0YTBjMjc1MjVmNTZiZWFhNzRmNzdhMjA4NWRiYWEiLCJ0IjoiZmQ1YWRjY2YtYzFiOC00ZTg5LTgzYTQtNzYyZThlYjFjNTNiIiwicyI6IlptVmpaR0k0TjJZdE5tUTBOUzAwTmpabUxXRXdNV1l0TXpkbVlqSTVNRGd6WW1SaiJ9

echo [3/3] Menunggu sinkronisasi koneksi ke Cloudflare (sekitar 7 detik)...
timeout /t 7 >nul

echo.
echo ============================================================
echo [SUKSES AKTIF 100%] Portal KKA SUDAH ONLINE!
echo.
echo Alamat Web Siswa & Guru:
echo 👉 https://portalkka.my.id
echo.
echo PENTING:
echo 1. Di taskbar bawah laptop Anda akan muncul 2 jendela kecil (Server & Tunnel).
echo 2. JANGAN TUTUP jendela tersebut selama jam mengajar/ujian berlangsung.
echo 3. Jendela ini boleh Anda tutup sekarang jika sudah selesai membaca.
echo ============================================================
echo.
echo Membuka website di browser secara otomatis...
start https://portalkka.my.id/login
pause
