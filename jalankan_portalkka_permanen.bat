@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Portal Pembelajaran KKA - SMAN 7 Pontianak (portalkka.my.id)

echo ============================================================
echo   PORTAL PEMBELAJARAN KKA FASE E - SMAN 7 PONTIANAK
echo   Domain Resmi: https://portalkka.my.id
echo ============================================================
echo.
echo [1/2] Menyalakan Server Lokal KKA...
start /b python run.py

timeout /t 3 >nul

echo [2/2] Menghubungkan Tunnel Resmi ke https://portalkka.my.id ...
start "" /b "bin\cloudflared.exe" tunnel run --token eyJhIjoiMGU0YTBjMjc1MjVmNTZiZWFhNzRmNzdhMjA4NWRiYWEiLCJ0IjoiZmQ1YWRjY2YtYzFiOC00ZTg5LTgzYTQtNzYyZThlYjFjNTNiIiwicyI6IlptVmpaR0k0TjJZdE5tUTBOUzAwTmpabUxXRXdNV1l0TXpkbVlqSTVNRGd6WW1SaiJ9

echo.
echo ============================================================
echo [SUKSES AKTIF] Portal KKA sudah ONLINE!
echo Alamat Web Siswa & Guru:
echo 👉 https://portalkka.my.id
echo.
echo JANGAN TUTUP JENDELA INI SELAMA JAM BELAJAR/UJIAN!
echo (Jika ditutup, server akan mati dan muncul Error 1033)
echo ============================================================
echo.
pause
