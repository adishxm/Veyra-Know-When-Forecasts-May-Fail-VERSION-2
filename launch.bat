@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

:: ═══════════════════════════════════════════════════════════════
::  HEXARK — Team Launch Script for Veyra Sentinel Platform
:: ═══════════════════════════════════════════════════════════════

title HEXARK — Veyra Sentinel Launcher
color 0B

echo.
echo  ██╗  ██╗███████╗██╗  ██╗ █████╗ ██████╗ ██╗  ██╗
echo  ██║  ██║██╔════╝╚██╗██╔╝██╔══██╗██╔══██╗██║ ██╔╝
echo  ███████║█████╗   ╚███╔╝ ███████║██████╔╝█████╔╝ 
echo  ██╔══██║██╔══╝   ██╔██╗ ██╔══██║██╔══██╗██╔═██╗ 
echo  ██║  ██║███████╗██╔╝ ██╗██║  ██║██║  ██║██║  ██╗
echo  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
echo.
echo  ══════════════════════════════════════════════════════
echo       VEYRA SENTINEL — Atmospheric Forecast Reliability
echo       Team HEXARK ^| SIH 2024 ^| Problem Statement 26079
echo  ══════════════════════════════════════════════════════
echo.

:: ─── Verify Python ──────────────────────────────────────────
echo  [*] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] ERROR: Python is not installed or not in PATH.
    echo      Please install Python 3.10+ and try again.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  [✓] %%v detected

:: ─── Verify Node.js ─────────────────────────────────────────
echo  [*] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] ERROR: Node.js is not installed or not in PATH.
    echo      Please install Node.js 18+ and try again.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('node --version 2^>^&1') do echo  [✓] Node.js %%v detected
echo.

:: ─── Install Python Dependencies ────────────────────────────
echo  [*] Installing Python dependencies...
pip install -r requirements.txt -q 2>nul
echo  [✓] Python dependencies ready
echo.

:: ─── Install Frontend Dependencies ──────────────────────────
echo  [*] Installing frontend dependencies...
if not exist "frontend\node_modules" (
    cd frontend
    call npm install --silent 2>nul
    cd ..
    echo  [✓] Frontend dependencies installed
) else (
    echo  [✓] Frontend dependencies already installed
)
echo.

:: ─── Start Backend Server ───────────────────────────────────
echo  ══════════════════════════════════════════════════════
echo   Starting Veyra Sentinel Backend (port 8000)...
echo  ══════════════════════════════════════════════════════
echo.
start "HEXARK — Backend" cmd /k "title HEXARK Backend ^| Port 8000 && color 0A && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

:: Wait for backend to initialize
echo  [*] Waiting for backend to start...
timeout /t 4 /nobreak >nul

:: ─── Start Frontend Dev Server ──────────────────────────────
echo  ══════════════════════════════════════════════════════
echo   Starting Veyra Dashboard Frontend (port 5173)...
echo  ══════════════════════════════════════════════════════
echo.
start "HEXARK — Frontend" cmd /k "title HEXARK Frontend ^| Port 5173 && color 0D && cd frontend && npm run dev"

:: Wait for frontend to initialize
echo  [*] Waiting for frontend to start...
timeout /t 5 /nobreak >nul

:: ─── Open Dashboard in Browser ──────────────────────────────
echo.
echo  ══════════════════════════════════════════════════════
echo   Opening Veyra Dashboard in your browser...
echo  ══════════════════════════════════════════════════════
start "" "http://127.0.0.1:5173/Veyra-Know-When-Forecasts-May-Fail/"

echo.
echo  ┌─────────────────────────────────────────────────────┐
echo  │                                                     │
echo  │   VEYRA SENTINEL is now running!                    │
echo  │                                                     │
echo  │   Backend:    http://127.0.0.1:8000                 │
echo  │   Frontend:   http://127.0.0.1:5173                 │
echo  │   API Docs:   http://127.0.0.1:8000/docs            │
echo  │                                                     │
echo  │   Press any key to stop all servers...              │
echo  │                                                     │
echo  └─────────────────────────────────────────────────────┘
echo.
pause >nul

:: ─── Cleanup ────────────────────────────────────────────────
echo.
echo  [*] Shutting down servers...
taskkill /FI "WINDOWTITLE eq HEXARK — Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK — Frontend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK Frontend*" /F >nul 2>&1
echo  [✓] All servers stopped. Goodbye!
echo.
