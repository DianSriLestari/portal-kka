@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Persiapan Portal KKA di PC Baru

echo ============================================================
echo   PERSIAPAN PORTAL KKA DI PC BARU
echo   SMAN 7 Pontianak (portalkka.my.id)
echo ============================================================
echo.

:: 1. Cek Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python belum terinstal atau belum dicentang 'Add Python to PATH'!
    echo.
    echo Silakan unduh dan instal Python dari: https://www.python.org/downloads/
    echo PENTING: Saat instal, centang kotak "Add Python.exe to PATH".
    echo.
    pause
    exit /b
)

echo [1/2] Python terdeteksi:
python --version
echo.

echo [2/2] Menginstal pustaka yang dibutuhkan (FastAPI, Uvicorn, Openpyxl, dll)...
pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo [SUKSES 100%] Semua komponen di PC baru siap digunakan!
    echo.
    echo Langkah selanjutnya:
    echo Cukup klik 2x file: jalankan_portalkka_permanen.bat
    echo Website https://portalkka.my.id akan langsung online dari PC ini!
    echo ============================================================
) else (
    echo.
    echo [PERINGATAN] Terjadi kendala saat mengunduh pustaka. Pastikan PC terkoneksi internet.
)

echo.
pause
