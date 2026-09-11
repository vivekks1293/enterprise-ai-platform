@echo off
title Enterprise AI Platform - START (ON SWITCH)
color 0A
cls
echo ================================================================
echo        ENTERPRISE AI PLATFORM - SAFE LOCAL DEPLOYMENT           
echo ================================================================
echo.
echo [*] Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [!] ERROR: Docker is not running!
    echo     Please start Docker Desktop on your PC and run this script again.
    echo.
    pause
    exit /b 1
)

echo [*] Starting isolated Docker containers...
echo     - Database: PostgreSQL 16 (Max 1GB RAM)
echo     - Backend:  FastAPI + PyTorch (Max 3.5GB RAM)
echo     - Frontend: Angular 18 + Nginx Gateway (Max 512MB RAM, Max 5 users)
echo     - Tunnel:   Cloudflare Secure Tunnel (No open router ports)
echo.

docker compose up -d --build

if %errorlevel% neq 0 (
    color 0C
    echo [!] ERROR: Failed to start containers. Check logs.
    pause
    exit /b 1
)

echo.
echo [*] Applying database migrations...
timeout /t 5 /nobreak >nul
docker compose exec backend uv run alembic upgrade head

echo.
echo ================================================================
echo                   SERVER IS LIVE AND ACTIVE!                   
echo ================================================================
echo.
echo   [Local Access] : http://localhost
echo.
echo [*] Fetching your secure Cloudflare Public URL...
timeout /t 5 /nobreak >nul

for /f "tokens=*" %%i in ('docker logs enterprise-ai-tunnel 2^>^&1 ^| findstr /i "trycloudflare.com"') do (
    echo   [Public Access]: %%i
)

echo.
echo ----------------------------------------------------------------
echo   SAFEGUARDS ACTIVE:
echo     - Max 5 concurrent connections enforced at gateway
echo     - Max 25MB per uploaded document
echo     - Hard RAM and CPU limits applied
echo     - Zero open ports on your home router
echo.
echo   TO TURN OFF: Simply double-click STOP_SERVER.bat
echo ----------------------------------------------------------------
echo.
pause

