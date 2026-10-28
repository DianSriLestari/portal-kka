@echo off
title Portal Pembelajaran KKA - Server Lokal & Cloudflare Tunnel Online
color 0A

echo ===============================================================================
echo     PORTAL PEMBELAJARAN KKA FASE E (SMAN 7 PONTIANAK) - ONLINE SYSTEM
echo ===============================================================================
echo.
echo [1/2] Menjalankan Server Backend FastAPI di http://127.0.0.1:8000...
start "Portal KKA - Backend Server" cmd /k "cd /d "%~dp0" && python run.py"

echo.
echo Menunggu server siap (3 detik)...
timeout /t 3 /nobreak >nul

echo.
echo [2/2] Membuka Cloudflare Tunnel Online Publik (HTTPS Gratis)...
echo Link publik akan muncul di jendela baru yang terbuka.
echo Anda dapat membagikan link tersebut ke siswa untuk diakses via HP/Laptop.
echo.
start "Portal KKA - Cloudflare Tunnel" cmd /k "cd /d "%~dp0" && bin\cloudflared.exe tunnel --url http://127.0.0.1:8000"

echo ===============================================================================
echo KEDUA PROSES TELAH BERJALAN!
echo - Jangan tutup jendela command prompt yang terbuka agar sistem tetap online.
echo - Siswa dan Guru dapat langsung mengakses portal melalui link yang tertera.
echo ===============================================================================
pause
