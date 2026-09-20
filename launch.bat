@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title HEXARK - Veyra Sentinel Launcher
cls

:: --- Display Fastfetch Dashboard ---
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python scripts\banner.py
)

:: --- Pre-flight System Checks ---
echo  ===================================================================
echo   Checking Environment & Dependencies...
echo  ===================================================================

:: Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [!] ERROR: Python is not found in your system PATH!
    echo      Please install Python 3.10+ from https://python.org/
    echo      and check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Check Node.js / npm
where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [!] ERROR: Node.js / npm is not found in your system PATH!
    echo      Please install Node.js (v18 or higher) from https://nodejs.org/
    echo      and restart this launcher.
    echo.
    pause
    exit /b 1
)

:: Check Backend Dependencies (uvicorn, fastapi)
python -c "import uvicorn, fastapi" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [*] First-time setup: Installing backend dependencies (pip install)...
    echo      This may take a moment, please wait...
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo  [!] WARNING: Some Python dependencies may have failed to install.
    )
    echo  [OK] Backend dependencies checked.
)

:: Check Frontend Dependencies (node_modules)
if not exist "frontend\node_modules\" (
    echo.
    echo  ===================================================================
    echo   First-time setup: 'frontend\node_modules' not found!
    echo   Installing frontend packages via 'npm install'...
    echo   This may take 1-2 minutes on first run, please wait...
    echo  ===================================================================
    cd /d "%~dp0frontend"
    call npm install
    cd /d "%~dp0"
    if not exist "frontend\node_modules\" (
        echo.
        echo  [!] ERROR: 'npm install' failed!
        echo      Please open a terminal in 'frontend' and run 'npm install' manually.
        echo.
        pause
        exit /b 1
    )
    echo  [OK] Frontend dependencies installed successfully!
    echo.
)

echo  [OK] All pre-flight checks passed.
echo.

:: --- Start Backend Server ---
echo  ===================================================================
echo   Starting Veyra Sentinel Backend [port 8000]...
echo  ===================================================================
start "HEXARK-Backend" cmd /k "title HEXARK-Backend && cd /d "%~dp0" && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

echo  [*] Waiting for backend to initialize...
ping 127.0.0.1 -n 4 >nul

:: --- Start Frontend Dev Server ---
echo.
echo  ===================================================================
echo   Starting Veyra Dashboard Frontend [port 5173]...
echo  ===================================================================
start "HEXARK-Frontend" cmd /k "title HEXARK-Frontend && cd /d "%~dp0frontend" && call npm run dev"

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
echo  ^|   Press any key in this window to stop all servers...           ^|
echo  ^|                                                                 ^|
echo  +-----------------------------------------------------------------+
echo.
pause >nul

:: --- Shutdown Servers ---
echo.
echo  [*] Shutting down servers and closing terminals...
taskkill /FI "WINDOWTITLE eq HEXARK-Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK-Frontend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK Frontend*" /T /F >nul 2>&1
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000,5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
echo  [OK] All servers and spawned terminals closed.
echo.
ping 127.0.0.1 -n 2 >nul
