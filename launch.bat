@echo off
cd /d "%~dp0"
title HEXARK - Veyra Sentinel Launcher
color 0B
cls

echo.
echo   ===================================================================
echo.
echo     #    #  ######  #    #    ##    #####   #    #
echo     #    #  #        #  #    #  #   #    #  #   # 
echo     ######  #####     ##    #    #  #####   ####  
echo     #    #  #         ##    ######  #  #    #  #  
echo     #    #  #        #  #   #    #  #   #   #   # 
echo     #    #  ######  #    #  #    #  #    #  #    #
echo.
echo   ===================================================================
echo         VEYRA SENTINEL - Atmospheric Forecast Reliability Platform
echo         Team HEXARK - SIH 2026 - Problem Statement 26079
echo   ===================================================================
echo.

:: --- Verify Python ---
echo  [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo         Please install Python 3.10+ and try again.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  [OK] %%v detected

:: --- Verify Node.js ---
echo  [*] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Node.js is not installed or not in PATH.
    echo         Please install Node.js 18+ and try again.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('node --version 2^>^&1') do echo  [OK] Node.js %%v detected
echo.

:: --- Verify Frontend Dependencies ---
if not exist "frontend\node_modules" (
    echo  [*] Installing frontend dependencies [first-time setup]...
    cd frontend
    call npm install
    cd ..
    echo  [OK] Frontend dependencies installed.
) else (
    echo  [OK] Frontend dependencies already installed.
)
echo.

:: --- Start Backend Server ---
echo  ===================================================================
echo   Starting Veyra Sentinel Backend [port 8000]...
echo  ===================================================================
start "HEXARK-Backend" cmd /k "title HEXARK Backend [Port 8000] && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

echo  [*] Waiting for backend to initialize...
ping 127.0.0.1 -n 4 >nul

:: --- Start Frontend Dev Server ---
echo.
echo  ===================================================================
echo   Starting Veyra Dashboard Frontend [port 5173]...
echo  ===================================================================
start "HEXARK-Frontend" cmd /k "title HEXARK Frontend [Port 5173] && cd frontend && npm run dev"

echo  [*] Waiting for frontend to initialize...
ping 127.0.0.1 -n 5 >nul

:: --- Open Dashboard in Browser ---
echo.
echo  ===================================================================
echo   Opening Veyra Dashboard in your browser...
echo  ===================================================================
start "" "http://127.0.0.1:5173/Veyra-Know-When-Forecasts-May-Fail/"

echo.
echo  +-----------------------------------------------------------------+
echo  ^|                                                                 ^|
echo  ^|   VEYRA SENTINEL is now running!                                ^|
echo  ^|                                                                 ^|
echo  ^|   Backend:    http://127.0.0.1:8000                             ^|
echo  ^|   Frontend:   http://127.0.0.1:5173                             ^|
echo  ^|   API Docs:   http://127.0.0.1:8000/docs                        ^|
echo  ^|                                                                 ^|
echo  ^|   Press any key in this window to stop all servers...           ^|
echo  ^|                                                                 ^|
echo  +-----------------------------------------------------------------+
echo.
pause >nul

:: --- Shutdown Servers ---
echo.
echo  [*] Shutting down servers...
taskkill /FI "WINDOWTITLE eq HEXARK-Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK-Frontend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK Frontend*" /F >nul 2>&1
echo  [OK] All servers stopped.
echo.
ping 127.0.0.1 -n 2 >nul
