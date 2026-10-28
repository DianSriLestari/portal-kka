@echo off
chcp 65001 >nul
title Upload Portal KKA ke GitHub untuk Render.com
echo ============================================================
echo   UPLOAD PORTAL KKA KE GITHUB (UNTUK RENDER.COM)
echo ============================================================
echo.
echo Pastikan Anda sudah membuat repository kosong di https://github.com/new
echo Contoh URL: https://github.com/username-anda/portal-kka.git
echo.
set /p REPO_URL="Masukkan URL Repository GitHub Anda: "

if "%REPO_URL%"=="" (
    echo [ERROR] URL Repository tidak boleh kosong!
    pause
    exit /b
)

echo.
echo Menghubungkan ke GitHub...
git branch -M main
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo Mengunggah kode ke GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo [SUKSES] Kode berhasil diunggah ke GitHub!
    echo Sekarang buka https://dashboard.render.com
    echo Klik "New +" -> "Web Service" -> Pilih repository Anda!
    echo ============================================================
) else (
    echo.
    echo [GAGAL] Terjadi kesalahan saat upload. Pastikan login GitHub Anda sesuai.
)
echo.
pause
