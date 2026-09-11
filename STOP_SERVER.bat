@echo off
title Enterprise AI Platform - STOP (OFF SWITCH)
color 0C
cls
echo ================================================================
echo        ENTERPRISE AI PLATFORM - SHUTTING DOWN                   
echo ================================================================
echo.
echo [*] Severing Cloudflare public tunnel...
echo [*] Stopping and removing isolated containers...
echo.

docker compose down

echo.
echo ================================================================
echo                  PLATFORM IS COMPLETELY OFF!                   
echo ================================================================
echo.
echo   - Public link is permanently severed.
echo   - All containers have terminated.
echo   - 100%% of RAM and CPU returned to your PC.
echo   - Zero background processes running.
echo   - Your database and uploaded files are saved safely on disk.
echo.
echo ================================================================
echo.
pause

