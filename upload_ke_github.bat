@echo off
chcp 65001 >nul
title Upload Portal KKA ke GitHub
echo ============================================================
echo   UPLOAD PORTAL KKA KE GITHUB (DianSriLestari/portal-kka)
echo ============================================================
echo.
echo Sedang mengunggah file ke https://github.com/DianSriLestari/portal-kka ...
echo.
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo [SUKSES 100%] Semua kode berhasil diunggah ke GitHub!
    echo.
    echo Langkah selanjutnya:
    echo 1. Buka https://dashboard.render.com
    echo 2. Klik "New +" -> "Web Service"
    echo 3. Pilih repository: DianSriLestari/portal-kka
    echo 4. Klik "Deploy"
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo [CATATAN] Jika diminta login, silakan klik Sign in with Browser.
    echo ============================================================
)
echo.
pause
