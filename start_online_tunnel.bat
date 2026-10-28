@echo off
title Cloudflare Tunnel - Portal KKA Online
echo =====================================================================
echo    PORTAL PEMBELAJARAN KKA FASE E - CLOUDFLARE TUNNEL ONLINE
echo    Membuka akses internet gratis via HTTPS aman ke localhost:8000
echo =====================================================================
echo.
echo Pastikan server portal ("python run.py") sudah berjalan di port 8000.
echo.
"%~dp0bin\cloudflared.exe" tunnel --url http://127.0.0.1:8000
pause
